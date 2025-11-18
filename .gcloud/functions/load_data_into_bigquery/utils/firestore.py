"""
© Ocado Group
Created on 18/11/2025 at 15:08:50(+00:00).
"""

import typing as t
from datetime import datetime, timezone

from google.cloud.bigquery import WriteDisposition
from google.cloud.firestore import (  # type: ignore[import-untyped]
    Client,
    Transaction,
    transactional,
)

from .settings import FIRESTORE_DB_ID, PROJECT_ID

if t.TYPE_CHECKING:
    from .chunk import ChunkMetadata


CLIENT = Client(project=PROJECT_ID, database=FIRESTORE_DB_ID)


class ChunkLoadState(t.TypedDict):
    """The data stored in the Firestore document."""

    latest_timestamp: datetime
    processed_chunks: t.Dict[str, bool]
    is_first_chunk_loaded: bool


def track_chunk(chunk_metadata: "ChunkMetadata") -> t.Optional[str]:
    """
    Atomically checks and updates the state for a table.
    This is idempotent and safe for retries.
    """

    doc_ref = CLIENT.collection("load_data_into_bigquery_state").document(
        chunk_metadata.bq_table_name
    )

    chunk_id = f"{chunk_metadata.obj_i_start}_{chunk_metadata.obj_i_end}"

    @transactional
    def update_in_transaction(transaction: Transaction):
        snapshot = doc_ref.get(transaction=transaction)

        # Get current state or create a default one.
        data: ChunkLoadState = (
            t.cast(ChunkLoadState, snapshot.to_dict())
            if snapshot.exists
            else {
                "latest_timestamp": datetime.min.replace(tzinfo=timezone.utc),
                "processed_chunks": {},
                "is_first_chunk_loaded": False,
            }
        )

        # Check for new export timestamp.
        if chunk_metadata.timestamp > data["latest_timestamp"]:
            print("New export timestamp detected. Resetting state.")
            data = {
                "latest_timestamp": chunk_metadata.timestamp,
                "processed_chunks": {},
                "is_first_chunk_loaded": False,
            }
        # Check for old export.
        elif chunk_metadata.timestamp < data["latest_timestamp"]:
            print("Chunk is from an old export. Skipping.")
            return None
        # Check for duplicate chunk (idempotency).
        elif chunk_id in data["processed_chunks"]:
            print(f"Chunk {chunk_id} has already been processed. Skipping.")
            return None

        write_disposition = WriteDisposition.WRITE_APPEND
        if (
            chunk_metadata.bq_table_write_mode == "overwrite"
            and not data["is_first_chunk_loaded"]
        ):
            print("This is the first chunk for an 'overwrite' job.")
            write_disposition = WriteDisposition.WRITE_TRUNCATE
            data["is_first_chunk_loaded"] = True

        # Mark this chunk as processed and save the state,
        data["processed_chunks"][chunk_id] = True

        transaction.set(doc_ref, data)

        return write_disposition

    return update_in_transaction(CLIENT.transaction())
