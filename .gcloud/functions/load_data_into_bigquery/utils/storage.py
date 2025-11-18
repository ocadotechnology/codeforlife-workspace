"""
© Ocado Group
Created on 18/11/2025 at 15:03:33(+00:00).
"""

import typing as t

from google.cloud.storage import Client  # type: ignore[import-untyped]

from .settings import PROJECT_ID

CLIENT = Client(project=PROJECT_ID)


class Blob:
    """The blob that triggered the event."""

    class Metadata(t.TypedDict):
        """The metadata of a blob."""

        processed_status: t.NotRequired[t.Literal["failed"]]

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

    @property
    def bucket_name(self):
        """The name of the bucket."""

        return t.cast(str, self._bucket.name)

    @property
    def name(self):
        """The name of the blob."""

        return t.cast(str, self._blob.name)

    def delete(self):
        """Deletes the blob from the bucket."""

        print(f"Deleting blob: {self.name}...")
        self._blob.delete()
        print(f"Successfully deleted {self.name}.")

    def set_processed_status_to_failed(self):
        """Moves the blob to the failed subdirectory for manual inspection."""

        metadata = self.metadata or {}
        metadata["processed_status"] = "failed"
        self._blob.metadata = metadata

        print(f"Updating blob metadata: {self.name}...")
        self._blob.patch()
        print(f"Updated blob metadata: {self.name}...")
