"""
© Ocado Group
Created on 18/11/2025 at 15:08:50(+00:00).
"""

import logging
import typing as t
from datetime import datetime

from google.cloud.firestore import (  # type: ignore[import-untyped]
    Client,
    Transaction,
    transactional,
)

from .settings import FIRESTORE_DB_ID, PROJECT_ID

if t.TYPE_CHECKING:
    from .chunk import ChunkMetadata


CLIENT = Client(project=PROJECT_ID, database=FIRESTORE_DB_ID)
COLLECTION = CLIENT.collection("load_data_into_bigquery_state")


class TableOverwriteState:
    """The state when overwriting a table in BQ.

    We achieve state tracking across multiple function calls using
    Firestore (FS), where a document is created per BQ table to track its state.

    State tracking is necessary to know if a BQ table should be overwritten or
    appended to. The data should be overwritten if the current chunk is the
    first chunk received from a more recent timestamp. The data should be
    should be appended if the current chunk is the 2nd+ chunk received from
    the latest timestamp.

    Using an atomic transaction with FS, we avoid this race condition:
    1. 2 chunks are created and trigger the function at the same time.
    2. both function calls read `was_first_chunk_loaded=False`;
    3. both function calls overwrite the data in the BQ table;
    4. both function calls write `was_first_chunk_loaded=True`;
    5. only the data from the last chunk loaded into BQ is saved.

    The race condition is avoided because if FS detects that the document has
    been written to (it will have a new version), it fails the transaction. It
    then retries the transaction from the start, reads the latest document and
    tries to write again.
    """

    class Data(t.TypedDict):
        """The data stored in the Firebase document."""

        latest_timestamp: datetime
        first_chunk_id: t.Optional[str]
        was_first_chunk_loaded: bool

    def __init__(self, chunk_metadata: "ChunkMetadata"):
        self._chunk_metadata = chunk_metadata

        self._doc_ref = COLLECTION.document(chunk_metadata.bq_table_name)

        # What we WANT the state to be if this is the first chunk.
        first_data: TableOverwriteState.Data = {
            "latest_timestamp": chunk_metadata.timestamp,
            "first_chunk_id": chunk_metadata.timestamp_id,
            "was_first_chunk_loaded": False,
        }

        # Initialize the local state to this (in case doc doesn't exist).
        self._data = first_data

        @transactional
        def update_in_transaction(transaction: Transaction):
            default_data = self._data
            if self._get_data(transaction):
                # Check if the chunk is from a new timestamp.
                if chunk_metadata.timestamp > self.latest_timestamp:
                    logging.info("New timestamp detected. Resetting state.")
                    self._data = first_data
                # Check if the chunk is the first in the current timestamp.
                elif (
                    chunk_metadata.timestamp == self.latest_timestamp
                    and self.first_chunk_id is None
                ):
                    logging.info("Claiming first spot.")
                    self._data["first_chunk_id"] = chunk_metadata.timestamp_id
                    self._data["was_first_chunk_loaded"] = False

            self._set_data(transaction)

        update_in_transaction(CLIENT.transaction())

    def _get_data(self, transaction: Transaction):
        """Gets the data from the latest snapshot of the document."""

        snapshot = self._doc_ref.get(transaction=transaction)
        if not snapshot.exists:
            return False

        self._data = t.cast(TableOverwriteState.Data, snapshot.to_dict())
        return True

    def _set_data(self, transaction: Transaction):
        """Sets the data in the document."""

        transaction.set(self._doc_ref, self._data)

    @property
    def latest_timestamp(self):
        """The latest timestamp from all received chunks."""

        return self._data["latest_timestamp"]

    @property
    def first_chunk_id(self):
        """The ID of the first chunk received for the latest timestamp."""

        return self._data["first_chunk_id"]

    @first_chunk_id.setter
    def first_chunk_id(self, value: t.Optional[str]):
        """Update the value in the Firestore document."""

        # Check value has changed.
        if self.first_chunk_id == value:
            return

        @transactional
        def update_in_transaction(transaction: Transaction):
            self._get_data(transaction)  # NOTE: snapshot should exist!

            self._data["first_chunk_id"] = value

            self._set_data(transaction)

        update_in_transaction(CLIENT.transaction())

    @property
    def was_first_chunk_loaded(self):
        """A flag designating whether the first chunk has been loaded yet."""

        return self._data["was_first_chunk_loaded"]

    @was_first_chunk_loaded.setter
    def was_first_chunk_loaded(self, value: bool):
        """Update the value in the Firestore document."""

        # Check value has changed.
        if self.was_first_chunk_loaded == value:
            return

        @transactional
        def update_in_transaction(transaction: Transaction):
            self._get_data(transaction)  # NOTE: snapshot should exist!

            self._data["was_first_chunk_loaded"] = value

            self._set_data(transaction)

        update_in_transaction(CLIENT.transaction())

    @property
    def chunk_is_old(self):
        """Check if the chunk is from a previous timestamp."""

        return self._chunk_metadata.timestamp < self.latest_timestamp

    @property
    def first_chunk_is_loading(self):
        """Check if the first chunk is still loading."""

        return not self.was_first_chunk_loaded and self.first_chunk_id != None

    @property
    def chunk_is_first(self):
        """Checks if the chunk is first to be loaded."""

        return self.first_chunk_id == self._chunk_metadata.timestamp_id
