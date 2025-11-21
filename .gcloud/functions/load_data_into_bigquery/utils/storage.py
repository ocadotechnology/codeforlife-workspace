"""
© Ocado Group
Created on 18/11/2025 at 15:03:33(+00:00).
"""

import logging
import typing as t

from google.cloud.storage import Client  # type: ignore[import-untyped]

from .settings import PROJECT_ID

CLIENT = Client(project=PROJECT_ID)

_ProcessedStatus = t.Literal["failed"]


class Blob:
    """The blob that triggered the event."""

    class Metadata(t.TypedDict):
        """The metadata of a blob."""

        processed_status: t.NotRequired[_ProcessedStatus]

    def __init__(self, data: t.Dict[str, t.Any]):
        self._bucket = CLIENT.bucket(bucket_name=data["bucket"])
        self._blob = self._bucket.blob(blob_name=data["name"])

        self._metadata_loaded = False  # Track lazy loading.

    @property
    def metadata(self):
        """The metadata of the blob."""

        if not self._metadata_loaded:
            self._blob.reload()
            self._metadata_loaded = True

        return t.cast(t.Optional[Blob.Metadata], self._blob.metadata)

    @metadata.setter
    def metadata(self, value: Metadata):
        """Sets the metadata of the blob."""

        self._blob.metadata = value

        logging.info("Updating blob metadata...")
        self._blob.patch()
        logging.info("Updated blob metadata.")

    @property
    def bucket_name(self):
        """The name of the bucket."""

        return t.cast(str, self._bucket.name)

    @property
    def name(self):
        """The name of the blob."""

        return t.cast(str, self._blob.name)

    @property
    def processed_status(self):
        return (self.metadata or {}).get("processed_status")

    @processed_status.setter
    def processed_status(self, value: _ProcessedStatus):
        """Moves the blob to the failed subdirectory for manual inspection."""

        # Check value has changed.
        if self.processed_status == value:
            return

        metadata = self.metadata or {}
        metadata["processed_status"] = value
        self.metadata = metadata

    def delete(self):
        """Deletes the blob from the bucket."""

        logging.info("Deleting blob...")
        self._blob.delete()
        logging.info("Deleted blob.")
