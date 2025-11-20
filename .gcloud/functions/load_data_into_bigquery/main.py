"""
© Ocado Group
Created on 13/11/2025 at 09:07:12(+00:00).

--------
Overview
--------
This function is called whenever a blob is uploaded to the dedicated data-export
bucket. The purpose of this bucket is to temporarily save CSV files that contain
the exported data from the database. This function's job is to import the data
from the CSVs into their respective BigQuery (BQ) tables and delete the CSVs.

These CSVs are created by our custom celery-task:
https://github.com/ocadotechnology/codeforlife-package-python/blob/main/codeforlife/tasks/data_warehouse.py

Note that the data is 'chunked' into multiple CSV files. It doesn't matter which
order these CSVs are imported in as they can always be ordered when querying BQ.

--------------
Error Handling
--------------
Known errors SHOULD be caught and logged without re-raising the error so that
the function can return early to avoid the retry policy from kicking in. For
example: if a BQ table does not exist, retrying the function will not change
that. Unknown errors SHOULD NOT be caught so the retry policy can kick in.
"""

import typing as t
from datetime import datetime, timezone

from cloudevents.http import CloudEvent
from functions_framework import cloud_event
from google.cloud import bigquery
from utils import (
    MAX_EVENT_AGE_SECONDS,
    Blob,
    ChunkMetadata,
    TableOverwriteState,
    load_data_into_bigquery,
)


def event_is_too_old(event: CloudEvent):
    """Check if the event is too old to be processed."""

    event_time: datetime = event["time"]
    if event_time.tzinfo is None:
        event_time = event_time.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    event_age = (now - event_time).total_seconds()
    return event_age > MAX_EVENT_AGE_SECONDS


@cloud_event
def main(event: CloudEvent):
    """The entrypoint."""

    blob = Blob(event.data)

    # Transform the blob's name to chunk metadata.
    chunk_metadata = ChunkMetadata.from_blob_name(blob.name)
    # If the blob does not conform to the expected naming convention, delete it.
    if not chunk_metadata:
        blob.delete()
        return

    # Check if event is too old to keep processing.
    if event_is_too_old(event):
        print("Event is too old. Dropping to prevent more retries.")
        if blob.processed_status != "failed":
            blob.processed_status = "failed"
        return

    # Check if blob has already been marked as failed.
    if blob.processed_status == "failed":
        print(f"Failed blob: {blob.name}. Skipping.")
        return

    print(f"Processing blob: {blob.name}")

    if chunk_metadata.bq_table_write_mode == "overwrite":
        table_overwrite_state = TableOverwriteState(chunk_metadata)

        # Check if the chunk is from a previous timestamp.
        if table_overwrite_state.chunk_is_old:
            print("Chunk is from a previous timestamp. Deleting.")
            blob.delete()
            return

        # Check if the first chunk is still being loaded.
        if (
            table_overwrite_state.first_chunk_is_loading
            and not table_overwrite_state.chunk_is_first
        ):
            raise RuntimeError(
                "The first chunk is still overriding the table. Retrying."
            )

        try:
            # Check if the data-chunk was successfully loaded into BQ.
            if load_data_into_bigquery(
                blob,
                chunk_metadata,
                write_disposition=(
                    bigquery.WriteDisposition.WRITE_APPEND
                    if table_overwrite_state.was_first_chunk_loaded
                    else bigquery.WriteDisposition.WRITE_TRUNCATE
                ),
            ):
                # Track if the first chunk was loaded.
                if not table_overwrite_state.was_first_chunk_loaded:
                    print(
                        "Loaded the first chunk in"
                        f" {chunk_metadata.bq_table_name} for timestamp"
                        f" {chunk_metadata.timestamp}."
                    )
                    TableOverwriteState.was_first_chunk_loaded = True

                blob.delete()
            else:
                blob.processed_status = "failed"
        except Exception as ex:
            # Unset the first chunk so another chunk can claim the spot.
            if (
                table_overwrite_state.first_chunk_is_loading
                and table_overwrite_state.chunk_is_first
            ):
                table_overwrite_state.first_chunk_id = None

            raise ex  # Reraise exception so it can retry.

    else:  # chunk_metadata.bq_table_write_mode == "append"
        # Check if the data-chunk was successfully loaded into BQ.
        if load_data_into_bigquery(
            blob,
            chunk_metadata,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        ):
            blob.delete()
        else:
            blob.processed_status = "failed"
