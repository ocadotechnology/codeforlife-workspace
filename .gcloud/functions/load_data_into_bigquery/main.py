import base64
import json
import logging

from google.cloud import bigquery
from google.cloud import storage
from google.api_core.exceptions import NotFound

# --- Configuration ---
# Set these as environment variables in the function
PROJECT_ID = "decent-digit-629"
DATASET_ID = "cfl_prod_copy"
BUCKET_NAME = "export-db-to-bucket"
# ---------------------


def main(event, context):
    """
    Triggered by a Pub/Sub message.
    The message 'data' is expected to be a base64-encoded JSON string.
    Example JSON: {"table_id": "person", "write_mode": "OVERWRITE"}
    """
    
    # 1. --- Parse the Pub/Sub Message ---
    try:
        if 'data' in event:
            message_data = base64.b64decode(event['data']).decode('utf-8')
            message_json = json.loads(message_data)
            
            table_id = message_json['table_id']
            write_mode = message_json.get('write_mode', 'OVERWRITE') # Default to OVERWRITE
        else:
            raise ValueError("No 'data' in Pub/Sub event.")

        logging.info(f"Starting job for table: {table_id} with write mode: {write_mode}")

    except Exception as e:
        logging.error(f"Error parsing Pub/Sub message: {e}")
        return  # Stop execution

    # 2. --- Set up BQ & GCS variables ---
    full_table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_id}"
    gcs_uri = f"gs://{BUCKET_NAME}/{table_id}/*.csv"
    gcs_prefix = f"{table_id}/" # For deletion

    # 3. --- Run the BigQuery Load Job ---
    client_bq = bigquery.Client(project=PROJECT_ID)

    # Set write disposition
    if write_mode == 'OVERWRITE':
        write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
    elif write_mode == 'INTO':
        write_disposition = bigquery.WriteDisposition.WRITE_APPEND
    else:
        logging.error(f"Invalid write_mode: {write_mode}. Aborting.")
        return

    # Configure the job. This is the key part!
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        write_disposition=write_disposition,
        time_zone='Etc/UTC',
        # This solves your 1/0 boolean problem
        autodetect=False 
    )

    try:
        logging.info(f"Starting BigQuery load job from {gcs_uri} to {full_table_id}...")
        load_job = client_bq.load_table_from_uri(
            gcs_uri,
            full_table_id,
            job_config=job_config
        )
        
        load_job.result()  # Wait for the job to complete
        logging.info(f"BigQuery load successful. Loaded {load_job.output_rows} rows.")

    except NotFound:
        logging.error(f"Error: Table {full_table_id} or GCS path {gcs_uri} not found.")
        return # Don't delete files if load failed
    except Exception as e:
        logging.error(f"Error during BigQuery load job: {e}")
        logging.error(f"Job details: {load_job.errors}")
        return  # Don't delete files if load failed

    # 4. --- Delete GCS Files (Only on Success) ---
    try:
        logging.info(f"Deleting files from GCS path: {gcs_prefix}...")
        client_gcs = storage.Client(project=PROJECT_ID)
        bucket = client_gcs.bucket(BUCKET_NAME)
        blobs_to_delete = list(bucket.list_blobs(prefix=gcs_prefix))
        
        deleted_count = 0
        for blob in blobs_to_delete:
            if blob.name.endswith(".csv"):
                blob.delete()
                deleted_count += 1
        
        logging.info(f"Successfully deleted {deleted_count} CSV file(s).")

    except Exception as e:
        logging.error(f"Error during GCS file deletion: {e}")
        # Note: The data is loaded, but cleanup failed.
        # You may want to set up monitoring for this.