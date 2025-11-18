"""
© Ocado Group
Created on 18/11/2025 at 15:11:10(+00:00).
"""

import typing as t

from google.api_core import exceptions as google_exceptions
from google.cloud.bigquery import Client, LoadJobConfig, SourceFormat

from .settings import BIGQUERY_DATASET_ID, PROJECT_ID

if t.TYPE_CHECKING:
    from .chunk import ChunkMetadata
    from .storage import Blob


CLIENT = Client(project=PROJECT_ID)


def load_data_into_bigquery(
    blob: "Blob",
    chunk_metadata: "ChunkMetadata",
    write_disposition: str,
):
    """Loads the date from the CSV file into BQ."""

    full_table_id = ".".join(
        [PROJECT_ID, BIGQUERY_DATASET_ID, chunk_metadata.bq_table_name]
    )

    try:
        print("Starting BigQuery load job.")

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
        print(f"BigQuery load successful. Loaded {load_job.output_rows} rows.")

        return True
    except google_exceptions.NotFound:
        print(f"Error: Table {full_table_id} not found.")

    return False
