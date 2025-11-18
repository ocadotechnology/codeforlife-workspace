"""
© Ocado Group
Created on 18/11/2025 at 15:07:02(+00:00).
"""

import typing as t
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ChunkMetadata:
    """All of the metadata used to track a chunk."""

    BqTableWriteMode = t.Literal["overwrite", "append"]

    bq_table_name: str  # name of BigQuery table
    bq_table_write_mode: BqTableWriteMode  # write mode for BigQuery table
    timestamp: datetime  # when the data export began
    obj_i_start: int  # object index span start
    obj_i_end: int  # object index span end

    @classmethod
    # pylint: disable-next=too-many-locals,too-many-return-statements
    def from_blob_name(cls, blob_name: str):
        """Extract the chunk metadata from a blob name."""

        def handle_error(msg: str):
            print(
                f'Skipping blob with invalid name: "{blob_name}". Reason: {msg}'
            )

        def handle_split(
            value: str,
            sep: str,
            parts_name: str,
            expected_part_count: int,
        ):
            parts = value.split(sep)
            if len(parts) != expected_part_count:
                return handle_error(
                    f"{parts_name} should have"
                    f" {expected_part_count} parts when split with"
                    f' "{sep}".'
                )

            return parts

        # E.g. "user__append/2025-01-01_00:00:00__0001_1000.csv"
        blob_name_parts = handle_split(
            blob_name,
            sep="/",
            parts_name="blob name",
            expected_part_count=2,
        )
        if not blob_name_parts:
            return None
        # "user__append", "2025-01-01_00:00:00__0001_1000.csv"
        folder_name, file_name = blob_name_parts

        folder_name_parts = handle_split(
            folder_name,
            sep="__",
            parts_name="folder name",
            expected_part_count=2,
        )
        if not folder_name_parts:
            return None
        # "user", "append"
        bq_table_name, bq_table_write_mode = folder_name_parts

        if not bq_table_name:
            return handle_error("Table name is blank.")

        bq_table_write_mode_values = ("overwrite", "append")
        if not bq_table_write_mode in bq_table_write_mode_values:
            return handle_error(
                f"Table write-mode must be one of {bq_table_write_mode_values}."
            )
        bq_table_write_mode = t.cast(
            ChunkMetadata.BqTableWriteMode, bq_table_write_mode
        )

        file_name_suffix = ".csv"
        if not file_name.endswith(file_name_suffix):
            return handle_error(
                f'File name should end with "{file_name_suffix}".'
            )
        # "2025-01-01_00:00:00__0001_1000"
        file_name = file_name.removesuffix(file_name_suffix)

        file_name_parts = handle_split(
            file_name,
            sep="__",
            parts_name="file name",
            expected_part_count=2,
        )
        if not file_name_parts:
            return None
        # "2025-01-01_00:00:00", "0001_1000"
        timestamp_fstr, obj_i_span_fstr = file_name_parts

        try:
            # datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
            timestamp = datetime.strptime(
                timestamp_fstr, "%Y-%m-%d_%H:%M:%S"
            ).replace(tzinfo=timezone.utc)
        except ValueError as error:
            return handle_error(str(error))

        obj_i_span_fstr_parts = handle_split(
            obj_i_span_fstr,
            sep="_",
            parts_name="object-index span",
            expected_part_count=2,
        )
        if not obj_i_span_fstr_parts:
            return None
        # "0001", "1000"
        obj_i_start_fstr, obj_i_end_fstr = obj_i_span_fstr_parts

        try:
            # 1, 1000
            obj_i_start, obj_i_end = int(obj_i_start_fstr), int(obj_i_end_fstr)
        except ValueError as error:
            return handle_error(str(error))

        if obj_i_start < 1:
            return handle_error("Object start-index is less than 1.")

        if obj_i_end < obj_i_start:
            return handle_error("Object end-index is less than the start.")

        return cls(
            bq_table_name=bq_table_name,
            bq_table_write_mode=bq_table_write_mode,
            timestamp=timestamp,
            obj_i_start=obj_i_start,
            obj_i_end=obj_i_end,
        )
