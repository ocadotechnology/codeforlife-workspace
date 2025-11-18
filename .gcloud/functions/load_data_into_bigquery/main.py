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

from datetime import datetime, timezone

from cloudevents.http import CloudEvent
from functions_framework import cloud_event
from utils import (
    MAX_EVENT_AGE_SECONDS,
    Blob,
    ChunkMetadata,
    load_data_into_bigquery,
    track_chunk,
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

    # If the event was first triggered too long ago, mark it as failed and stop.
    if event_is_too_old(event):
        print("Event is too old. Dropping to prevent more retries.")
        if (
            not blob.metadata
            or blob.metadata.get("processed_status") != "failed"
        ):
            blob.set_processed_status_to_failed()
        return

    # If the function was triggered by a failed blob,
    if blob.metadata and blob.metadata.get("processed_status") == "failed":
        print(f"Failed blob: {blob.name}. Skipping.")
        return

    print(f"Processing blob: {blob.name}")

    # Track the chunk's state.
    write_disposition = track_chunk(chunk_metadata)
    # If the chunk should not be loaded into BQ, delete it.
    if not write_disposition:
        blob.delete()
        return

    # If the chunk's data is successfully loaded into BQ, delete it.
    if load_data_into_bigquery(blob, chunk_metadata, write_disposition):
        blob.delete()
    else:
        blob.set_processed_status_to_failed()
