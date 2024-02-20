# This file has been modified by the Nextpy Team in 2023 using AI tools and automation scripts. 
# We have rigorously tested these modifications to ensure reliability and performance. Based on successful test results, we are confident in the quality and stability of these changes.

"""Rss reader."""

from typing import List

from nextpy.ai.rag.document_loaders.basereader import BaseReader
from nextpy.ai.schema import DocumentNode


class RssReader(BaseReader):
    """RSS reader.

    Reads content from an RSS feed.

    """

    def __init__(self, html_to_text: bool = False) -> None:
        """Initialize with parameters.

        Args:
            html_to_text (bool): Whether to convert HTML to text.
                Requires `html2text` package.

        """
        try:
            import feedparser  # noqa: F401
        except ImportError:
            raise ValueError(
                "`feedparser` package not found, please run `pip install feedparser`"
            )

        if html_to_text:
            try:
                import html2text  # noqa: F401
            except ImportError:
                raise ValueError(
                    "`html2text` package not found, please run `pip install html2text`"
                )
        self._html_to_text = html_to_text

    def load_data(self, urls: List[str]) -> List[DocumentNode]:
        """Load data from RSS feeds.

        Args:
            urls (List[str]): List of RSS URLs to load.

        Returns:
            List[DocumentNode]: List of documents.

        """
        import feedparser

        if not isinstance(urls, list):
            raise ValueError("urls must be a list of strings.")

        documents = []

        for url in urls:
            parsed = feedparser.parse(url)
            for entry in parsed.entries:
                if "content" in entry:
                    data = entry.content[0].value
                else:
                    data = entry.description or entry.summary

                if self._html_to_text:
                    import html2text

                    data = html2text.html2text(data)

                metadata = {"title": entry.title, "link": entry.link}
                documents.append(DocumentNode(text=data, extra_info=metadata))

        return documents
