"""
© Ocado Group
Created on 18/11/2025 at 15:11:10(+00:00).
"""

import logging
import typing as t

from google.api_core import exceptions as google_exceptions
from google.cloud.bigquery import Client, LoadJobConfig, SourceFormat

from .settings import BIGQUERY_DATASET_ID, PROJECT_ID

if t.TYPE_CHECKING:
    from .chunk import ChunkMetadata
    from .storage import Blob


CLIENT = Client(project=PROJECT_ID)


def load_data_into_bigquery_table(
    blob: "Blob",
    chunk_metadata: "ChunkMetadata",
    write_disposition: str,
):
    """Loads the data from the CSV file into BigQuery.

    Args:
        blob: The blob to load the data from.
        chunk_metadata: The metadata of the chunk.
        write_disposition: The write-mode for the current chunk.

    Returns:
        A flag designating whether the flag was successfully processed. False
        will be returned if a known error occurred which makes it impossible to
        load the data (e.g. the BQ table does not exist) to avoid pointlessly
        retries.
    """

    full_table_id = ".".join(
        [PROJECT_ID, BIGQUERY_DATASET_ID, chunk_metadata.bq_table_name]
    )

    try:
        logging.info("Starting BigQuery load job.")

        load_job = CLIENT.load_table_from_uri(
            source_uris=f"gs://{blob.bucket_name}/{blob.name}",
            destination=full_table_id,
            job_config=LoadJobConfig(
                source_format=SourceFormat.CSV,
                skip_leading_rows=1,
                write_disposition=write_disposition,
                time_zone="Etc/UTC",
                date_format="YYYY-MM-DD",
                time_format="HH24:MI:SS",
                datetime_format="YYYY-MM-DD HH24:MI:SS",
            ),
        )

        load_job.result()
        logging.info(
            f"BigQuery load successful. Loaded {load_job.output_rows} rows."
        )

        return True
    except google_exceptions.NotFound:
        logging.error("Table %s not found. Unable to proceed.", full_table_id)

    return False
