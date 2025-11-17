"""
© Ocado Group
Created on 13/11/2025 at 09:07:12(+00:00).

--------
Overview
--------
This function is called whenever a blob is uploaded to the dedicated data-export
bucket. The purpose of this bucket is to temporarily save CSV files that contain
the exported data from the database. This function's job is to import the data
from CSVs into their respective BigQuery (BQ) tables and delete the CSVs.

These CSV data-exports are created by our custom celery-task:
https://github.com/ocadotechnology/codeforlife-package-python/blob/main/codeforlife/tasks/data_warehouse.py

Note that the data is 'chunked' into multiple CSV files. It doesn't matter which
order these CSVs are imported in.

--------------
State Tracking
--------------
Given that this function is stateless, we're using Firestore to track the state.
When importing a chunk, we first check if that chunk is from the current
timestamp and if so, we count how many chunks from that timestamp have been
successfully imported. In the case, were the BQ table's write-mode is
"overwrite", we do NOT import the data from previous chunks and just simply
delete them.

--------------
Error Handling
--------------
Known errors SHOULD be caught and logged without re-raising the error so that
the function can return early to avoid the retry policy from kicking in. For
example: if a BQ table does not exist, retrying the function will not change
that. Unknown errors SHOULD NOT be caught so the retry policy can kick in.

---------------------
CSV Naming Convention
---------------------
The CSVs follow a naming convention which affects the way this function runs.
  "{table_id}__{table_write_mode}/{timestamp}__{obj_i_start}_{obj_i_end}.csv"
- table_id: the table in BigQuery where this data is to be imported
- table_write_mode: whether to overwrite or append to the BQ table.
- timestamp: when the export was triggered.
- obj_i_start: The start of the object-index range.
- obj_i_end: The end of the object-index range.

For example: "user__append/2025-01-01_00:00:00__0001_1000.csv"
- table_id: the data is to imported into the "user" table in BQ.
- table_write_mode: the data is to be appended to the end of the BQ table.
- timestamp: the export was triggered on 2025-01-01 at 00:00:00.
- obj_i_start: the data is from row/object 1.
- obj_i_end: the data is to row/object 1000.
"""

import typing as t
from dataclasses import dataclass
from datetime import datetime, timezone

from cloudevents.http import CloudEvent
from functions_framework import cloud_event
from google.api_core import exceptions as google_exceptions
from google.cloud import bigquery, firestore, storage

# --- Configuration ---
PROJECT_ID = "decent-digit-629"
DATASET_ID = "cfl_prod_copy"
# ---------------------


@dataclass(frozen=True)
class Blob:
    """The blob that triggered the event."""

    bucket: str
    name: str

    def delete(self):
        """Deletes the blob from the bucket."""

        print(f"Deleting blob: {self.name}...")

        storage.Client(project=PROJECT_ID).bucket(self.bucket).blob(
            self.name
        ).delete()

        print(f"Successfully deleted {self.name}.")


BqTableWriteMode = t.Literal["overwrite", "append"]


@dataclass(frozen=True)
class ChunkMetadata:
    """All of the metadata used to track a chunk."""

    bq_table_name: str  # name of BigQuery table
    bq_table_write_mode: BqTableWriteMode  # write mode for BigQuery table
    timestamp: datetime  # when the data export began
    obj_i_start: int  # object index span start
    obj_i_end: int  # object index span end

    @classmethod
    # pylint: disable-next=too-many-locals,too-many-return-statements
    def from_blob_name(cls, blob_name: str):
        """Extract the chunk metadata from a blob name."""

        def handle_error(msg: str):
            print(
                f'Skipping blob with invalid name: "{blob_name}". Reason: {msg}'
            )

        def handle_split(
            value: str,
            sep: str,
            parts_name: str,
            expected_part_count: int,
        ):
            parts = value.split(sep)
            if len(parts) != expected_part_count:
                return handle_error(
                    f"{parts_name} should have"
                    f" {expected_part_count} parts when split with"
                    f' "{sep}".'
                )

            return parts

        # E.g. "user__append/2025-01-01_00:00:00__0001_1000.csv"
        blob_name_parts = handle_split(
            blob_name,
            sep="/",
            parts_name="blob name",
            expected_part_count=2,
        )
        if not blob_name_parts:
            return None
        # "user__append", "2025-01-01_00:00:00__0001_1000.csv"
        folder_name, file_name = blob_name_parts

        folder_name_parts = handle_split(
            folder_name,
            sep="__",
            parts_name="folder name",
            expected_part_count=2,
        )
        if not folder_name_parts:
            return None
        # "user", "append"
        bq_table_name, bq_table_write_mode = folder_name_parts

        if not bq_table_name:
            return handle_error("Table name is blank.")

        bq_table_write_mode_values = ("overwrite", "append")
        if not bq_table_write_mode in bq_table_write_mode_values:
            return handle_error(
                f"Table write-mode must be one of {bq_table_write_mode_values}."
            )
        bq_table_write_mode = t.cast(BqTableWriteMode, bq_table_write_mode)

        file_name_suffix = ".csv"
        if not file_name.endswith(file_name_suffix):
            return handle_error(
                f'File name should end with "{file_name_suffix}".'
            )
        # "2025-01-01_00:00:00__0001_1000"
        file_name = file_name.removesuffix(file_name_suffix)

        file_name_parts = handle_split(
            file_name,
            sep="__",
            parts_name="file name",
            expected_part_count=2,
        )
        if not file_name_parts:
            return None
        # "2025-01-01_00:00:00", "0001_1000"
        timestamp_fstr, obj_i_span_fstr = file_name_parts

        try:
            # datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
            timestamp = datetime.strptime(
                timestamp_fstr, "%Y-%m-%d_%H:%M:%S"
            ).replace(tzinfo=timezone.utc)
        except ValueError as error:
            return handle_error(str(error))

        obj_i_span_fstr_parts = handle_split(
            obj_i_span_fstr,
            sep="_",
            parts_name="object-index span",
            expected_part_count=2,
        )
        if not obj_i_span_fstr_parts:
            return None
        # "0001", "1000"
        obj_i_start_fstr, obj_i_end_fstr = obj_i_span_fstr_parts

        try:
            # 1, 1000
            obj_i_start, obj_i_end = int(obj_i_start_fstr), int(obj_i_end_fstr)
        except ValueError as error:
            return handle_error(str(error))

        if obj_i_start < 1:
            return handle_error("Object start-index is less than 1.")

        if obj_i_end < obj_i_start:
            return handle_error("Object end-index is less than the start.")

        return cls(
            bq_table_name=bq_table_name,
            bq_table_write_mode=bq_table_write_mode,
            timestamp=timestamp,
            obj_i_start=obj_i_start,
            obj_i_end=obj_i_end,
        )


class OverwriteState:
    """The state when overwriting the BigQuery table."""

    firestore_collection = "load_data_into_bigquery_state"

    class Data(t.TypedDict):
        """The data stored in the Firestore document."""

        latest_timestamp: datetime
        loaded_first_chunk: bool

    _data: Data

    @property
    def latest_timestamp(self):
        return self._data["latest_timestamp"]

    @property
    def loaded_first_chunk(self):
        return self._data["loaded_first_chunk"]

    def __init__(self, chunk_metadata: ChunkMetadata):
        """
        Use the Firestore document to track the latest timestamp and whether the
        current chunk is the first to be loaded into BigQuery.
        """

        self.chunk_metadata = chunk_metadata

        self.firestore_client = firestore.Client(project=PROJECT_ID)
        self.firestore_doc_ref = self.firestore_client.collection(
            self.firestore_collection
        ).document(chunk_metadata.bq_table_name)

        @firestore.transactional
        def update_in_transaction(transaction: firestore.Transaction):
            doc_snapshot = self.firestore_doc_ref.get(transaction=transaction)

            data: OverwriteState.Data = (
                t.cast(OverwriteState.Data, doc_snapshot.to_dict())
                if doc_snapshot.exists
                else {
                    "latest_timestamp": datetime.min.replace(
                        tzinfo=timezone.utc
                    ),
                    "loaded_first_chunk": False,
                }
            )

            # Check if this is a new export.
            if self.chunk_metadata.timestamp > data["latest_timestamp"]:
                print("New export timestamp detected.")
                data = {
                    "latest_timestamp": self.chunk_metadata.timestamp,
                    "loaded_first_chunk": False,
                }

            transaction.set(self.firestore_doc_ref, data)

            return data

        self._data = update_in_transaction(self.firestore_client.transaction())

    def loaded_data(self):
        """
        Use the Firestore document to track if we have finished loading the data
        from the first chunk.
        """

        if self._data["loaded_first_chunk"]:
            return
        self._data["loaded_first_chunk"] = True

        @firestore.transactional
        def update_in_transaction(transaction: firestore.Transaction):
            transaction.set(self.firestore_doc_ref, self._data)

        update_in_transaction(self.firestore_client.transaction())


def load_data_into_bigquery(
    blob: Blob,
    chunk_metadata: ChunkMetadata,
    write_disposition: str,
):
    """Loads the date from the CSV file into BQ."""

    client = bigquery.Client(project=PROJECT_ID)
    full_table_id = ".".join(
        [PROJECT_ID, DATASET_ID, chunk_metadata.bq_table_name]
    )

    try:
        print("Starting BigQuery load job.")

        load_job = client.load_table_from_uri(
            source_uris=f"gs://{blob.bucket}/{blob.name}",
            destination=full_table_id,
            job_config=bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1,
                write_disposition=write_disposition,
                time_zone="Etc/UTC",
                date_format="YYYY-MM-DD",
                time_format="HH24:MI:SS",
                datetime_format="YYYY-MM-DD HH24:MI:SS",
            ),
        )

        load_job.result()
        print(f"BigQuery load successful. Loaded {load_job.output_rows} rows.")

        return True
    except google_exceptions.NotFound:
        print(f"Error: Table {full_table_id} not found.")

    # TODO: move to blob to a 'failed' subdirectory for manual review.

    return False


@cloud_event
def main(event: CloudEvent):
    """The entrypoint."""

    blob = Blob(bucket=event.data["bucket"], name=event.data["name"])

    print(f"Processing blob: {blob.name}")

    # Transform the blob's name to chunk metadata.
    chunk_metadata = ChunkMetadata.from_blob_name(blob.name)

    # Check if the blob does not conform to the expected naming convention.
    if not chunk_metadata:
        blob.delete()

    # Else check if the chunk's data is to be loaded into BQ in overwrite mode.
    elif chunk_metadata.bq_table_write_mode == "overwrite":
        # Track the overwrite's state.
        state = OverwriteState(chunk_metadata)

        # Check if this chunk is from a previous timestamp.
        if chunk_metadata.timestamp < state.latest_timestamp:
            print("Chunk is from an old export. Skipping.")
            blob.delete()

        # Else check if the chunk's data was successfully loaded into BQ.
        elif load_data_into_bigquery(
            blob,
            chunk_metadata,
            write_disposition=(
                bigquery.WriteDisposition.WRITE_APPEND
                if state.loaded_first_chunk
                else bigquery.WriteDisposition.WRITE_TRUNCATE
            ),
        ):
            state.loaded_data()
            blob.delete()

    # Else check if the chunk's data was successfully loaded into BQ.
    elif load_data_into_bigquery(  # bq_table_write_mode == "append"
        blob,
        chunk_metadata,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    ):
        blob.delete()
