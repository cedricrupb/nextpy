# This file has been modified by the Nextpy Team in 2023 using AI tools and automation scripts. 
# We have rigorously tested these modifications to ensure reliability and performance. Based on successful test results, we are confident in the quality and stability of these changes.

"""Paged CSV reader.

A parser for tabular data files.

"""
from pathlib import Path
from typing import Any, Dict, List, Optional

from nextpy.ai.rag.document_loaders.basereader import BaseReader
from nextpy.ai.schema import DocumentNode


class PagedCSVReader(BaseReader):
    """Paged CSV parser.

    Displayed each row in an LLM-friendly format on a separate DocumentNode.

    Args:
        encoding (str): Encoding used to open the file.
            utf-8 by default.
    """

    def __init__(self, *args: Any, encoding: str = "utf-8", **kwargs: Any) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self._encoding = encoding

    def load_data(
        self, file: Path, extra_info: Optional[Dict] = None
    ) -> List[DocumentNode]:
        """Parse file."""
        import csv

        docs = []
        with open(file, "r", encoding=self._encoding) as fp:
            csv_reader = csv.DictReader(fp)  # type: ignore
            for row in csv_reader:
                docs.append(
                    DocumentNode(
                        text="\n".join(
                            f"{k.strip()}: {v.strip()}" for k, v in row.items()
                        ),
                        extra_info=extra_info or {},
                    )
                )
        return docs
