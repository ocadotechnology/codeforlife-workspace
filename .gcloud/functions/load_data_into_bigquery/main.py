"""
© Ocado Group
Created on 13/11/2025 at 09:07:12(+00:00).

--------
Overview
--------

This function is called whenever a blob is uploaded to the dedicated data-export
bucket. The purpose of this function is to load the data from the CSVs (that are
uploaded into the bucket) into their destined BigQuery (BQ) tables and delete
the CSVs.

These CSVs are created by our custom celery-task:
https://github.com/ocadotechnology/codeforlife-package-python/blob/main/codeforlife/tasks/data_warehouse.py

Each CSV file is a data-chunk of a data-export. That is, a subset of rows from a
queryset that was first triggered in a job whose purpose it is to export the
data.

-------------
Data Ordering
-------------

CSVs are not guaranteed to be imported in any particular order. It's
assumed that the data contains the necessary fields to order it when querying a
BQ table.

--------------
Error Handling
--------------

Known errors SHOULD be caught and logged without re-raising the error so that
the function can return early to avoid the retry policy from kicking in. For
example: if a BQ table does not exist, retrying the function will not change
that. Unknown errors SHOULD NOT be caught so the retry policy can kick in.
"""

import logging
import typing as t
from datetime import datetime, timezone

from cloudevents.http import CloudEvent
from functions_framework import cloud_event
from google.cloud import bigquery
from utils import (
    LOG_CONTEXT,
    MAX_EVENT_AGE_SECONDS,
    Blob,
    ChunkMetadata,
    TableOverwriteState,
    load_data_into_bigquery_table,
)


def event_is_too_old(event: CloudEvent):
    """Check if the event is too old to be processed."""

    tz = timezone.utc
    event_time: t.Union[str, datetime] = event["time"]
    if isinstance(event_time, str):
        event_time = datetime.fromisoformat(
            event_time.replace("Z", "+00:00")
        ).replace(tzinfo=tz)
    elif event_time.tzinfo is None:
        event_time = event_time.replace(tzinfo=tz)

    now = datetime.now(tz)
    event_age = (now - event_time).total_seconds()
    return event_age > MAX_EVENT_AGE_SECONDS


def process_blob(blob: Blob):
    """Process the blob."""

    # Transform the blob's name to chunk metadata.
    chunk_metadata = ChunkMetadata.from_blob_name(blob.name)
    # Check if blob conforms to the naming convention.
    if not chunk_metadata:
        blob.delete()
        return

    if chunk_metadata.bq_table_write_mode == "overwrite":
        table_overwrite_state = TableOverwriteState(chunk_metadata)

        # Check if the chunk is from a previous timestamp.
        if table_overwrite_state.chunk_is_old:
            logging.info("Chunk is from a previous timestamp. Deleting.")
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
            if load_data_into_bigquery_table(
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
                    print("The first chunk has overwritten the table.")
                    table_overwrite_state.was_first_chunk_loaded = True

                blob.delete()
            else:
                blob.processed_status = "failed"
        except Exception as ex:
            # Unset the first chunk so another chunk can claim the spot.
            if (
                table_overwrite_state.first_chunk_is_loading
                and table_overwrite_state.chunk_is_first
            ):
                logging.info("Releasing claim on first spot and retrying.")
                table_overwrite_state.first_chunk_id = None

            raise ex  # Reraise exception so it can retry.

    else:  # chunk_metadata.bq_table_write_mode == "append"
        # Check if the data-chunk was successfully loaded into BQ.
        if load_data_into_bigquery_table(
            blob,
            chunk_metadata,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        ):
            blob.delete()
        else:
            blob.processed_status = "failed"


@cloud_event
def main(event: CloudEvent):
    """The entrypoint."""

    blob = Blob(event.data)

    # Provide context for each log.
    token = LOG_CONTEXT.set(
        {
            "event_id": event["id"],
            "bucket_name": blob.bucket_name,
            "blob_name": blob.name,
        }
    )

    try:
        # Check if event is too old to be processed.
        if event_is_too_old(event):
            logging.info("Event is too old. Dropping to prevent more retries.")
            if blob.processed_status != "failed":
                blob.processed_status = "failed"
            return

        # Check if blob has already been marked as failed.
        if blob.processed_status == "failed":
            logging.info("Blob's processed-status is 'failed'. Skipping.")
            return

        process_blob(blob)
    finally:
        LOG_CONTEXT.reset(token)
