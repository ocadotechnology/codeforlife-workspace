"""
© Ocado Group
Created on 18/11/2025 at 15:17:25(+00:00).
"""

import os

# Project.
PROJECT_ID = "decent-digit-629"

# Event.
MAX_EVENT_AGE_SECONDS = 60 * 60

# Firestore.
FIRESTORE_DB_ID = os.environ["FIRESTORE_DB_ID"]

# BigQuery.
BIGQUERY_DATASET_ID = os.environ["BIGQUERY_DATASET_ID"]
