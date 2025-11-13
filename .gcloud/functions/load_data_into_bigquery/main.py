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
from functions_framework import cloudevent
from google.api_core import exceptions as google_exceptions
from google.cloud import bigquery, firestore, storage

# --- Configuration ---
PROJECT_ID = "decent-digit-629"
DATASET_ID = "cfl_prod_copy"
FIRESTORE_COLLECTION = "load_data_into_bigquery_state"
# ---------------------


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

        if not bq_table_write_mode in ("overwrite", "append"):
            return handle_error("")
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


TrackChunkReturn = t.Tuple[bool, int]


def track_chunk(chunk_metadata: ChunkMetadata) -> TrackChunkReturn:
    """
    Atomically checks and updates the latest timestamp for a table.
    Returns True if the function should proceed (file is newer).
    Returns False if the file is a duplicate or out-of-order.
    """
    client = firestore.Client(project=PROJECT_ID)
    doc_ref = client.collection(FIRESTORE_COLLECTION).document(
        chunk_metadata.bq_table_name
    )

    @firestore.transactional
    def update_in_transaction(
        transaction: firestore.Transaction, doc_ref: firestore.DocumentReference
    ) -> TrackChunkReturn:
        snapshot = doc_ref.get(transaction=transaction)
        if snapshot.exists:
            latest_timestamp: datetime = snapshot.get("latest_timestamp")
            chunk_count: int = snapshot.get("chunk_count")

            if chunk_metadata.timestamp < latest_timestamp:
                is_latest_timestamp = False
            else:
                is_latest_timestamp = True
                if latest_timestamp < chunk_metadata.timestamp:
                    latest_timestamp = chunk_metadata.timestamp
                    chunk_count = 1
                else:  # latest_timestamp == chunk_metadata.timestamp
                    chunk_count += 1
        else:
            is_latest_timestamp = True
            latest_timestamp = chunk_metadata.timestamp
            chunk_count = 1

        transaction.set(
            doc_ref,
            {
                "latest_timestamp": latest_timestamp,
                "chunk_count": chunk_count,
            },
        )

        return is_latest_timestamp, chunk_count

    return update_in_transaction(client.transaction(), doc_ref)


def load_data_into_bigquery(
    bucket_name: str,
    blob_name: str,
    table_id: str,
    write_disposition: str,
):
    """Loads the date from the CSV file into BQ."""

    client = bigquery.Client(project=PROJECT_ID)
    full_table_id = ".".join([PROJECT_ID, DATASET_ID, table_id])

    try:
        print("Starting BigQuery load job.")

        load_job = client.load_table_from_uri(
            source_uris=f"gs://{bucket_name}/{blob_name}",
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

    return False


def delete_blob_from_bucket(bucket_name: str, blob_name: str):
    """Deletes the blob from the bucket.

    If an exception is raised during the deletion, we catch it to avoid retrying
    the entire workflow and subsequently writing the data to the BQ table again.
    """
    try:
        print(f"Deleting file: {blob_name}...")

        client = storage.Client(project=PROJECT_ID)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()

        print(f"Successfully deleted {blob_name}.")

    # pylint: disable-next=broad-exception-caught
    except Exception as ex:
        print(f"Error during GCS file deletion: {ex}")


@cloudevent
def main(event: CloudEvent):
    """The entrypoint."""

    bucket_name: str = event.data["bucket"]
    blob_name: str = event.data["name"]

    if not blob_name.endswith(".csv"):
        print(f"File {blob_name} is not a CSV. Ignoring.")
        return

    print(f"Processing file: {blob_name}")

    chunk_metadata = ChunkMetadata.from_blob_name(blob_name)
    if chunk_metadata:
        is_latest_timestamp, chunk_count = track_chunk(chunk_metadata)

        if not is_latest_timestamp:
            print(f"File {blob_name} is from a previous timestamp. Ignoring.")
            # Note: We do NOT delete the file, as it's an old one.
            # You could add logic here to delete it if you want.
            return

        data_was_loaded_into_bigquery = load_data_into_bigquery(
            bucket_name=bucket_name,
            blob_name=blob_name,
            table_id=chunk_metadata.bq_table_name,
            write_disposition=(
                bigquery.WriteDisposition.WRITE_APPEND
                if chunk_metadata.bq_table_write_mode == "append"
                or chunk_count == 1
                else bigquery.WriteDisposition.WRITE_TRUNCATE
            ),
        )

        if not data_was_loaded_into_bigquery:
            return

    delete_blob_from_bucket(bucket_name=bucket_name, blob_name=blob_name)
