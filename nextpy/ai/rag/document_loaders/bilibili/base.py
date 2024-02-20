# This file has been modified by the Nextpy Team in 2023 using AI tools and automation scripts. 
# We have rigorously tested these modifications to ensure reliability and performance. Based on successful test results, we are confident in the quality and stability of these changes.

"""Simple Reader that reads transcript and general infor of Bilibili video."""
import warnings
from typing import Any, List

from nextpy.ai.rag.document_loaders.basereader import BaseReader
from nextpy.ai.schema import DocumentNode


class BilibiliTranscriptReader(BaseReader):
    """Bilibili Transcript and video info reader."""

    @staticmethod
    def get_bilibili_info_and_subs(bili_url):
        import json
        import re

        import requests
        from bilibili_api import sync, video

        bvid = re.search(r"BV\w+", bili_url).group()
        # Create credential object
        v = video.Video(bvid=bvid)
        # Get video info and basic infor
        video_info = sync(v.get_info())
        title = video_info["title"]
        desc = video_info["desc"]

        # Get subtitle url
        sub_list = video_info["subtitle"]["list"]
        if sub_list:
            sub_url = sub_list[0]["subtitle_url"]
            result = requests.get(sub_url)
            raw_sub_titles = json.loads(result.content)["body"]
            raw_transcript = " ".join([c["content"] for c in raw_sub_titles])
            # Add basic video info to transcript
            raw_transcript_with_meta_info = f"Video Title: {title}, description: {desc}\nTranscript: {raw_transcript}"
            return raw_transcript_with_meta_info
        else:
            raw_transcript = ""
            warnings.warn(
                f"No subtitles found for video: {bili_url}. Return Empty transcript."
            )
            return raw_transcript

    def load_data(
        self, video_urls: List[str], **load_kwargs: Any
    ) -> List[DocumentNode]:
        """Load auto generated Video Transcripts from Bilibili, including additional metadata.

        Args:
            video_urls (List[str]): List of Bilibili links for which transcripts are to be read.

        Returns:
            List[DocumentNode]: A list of DocumentNode objects, each containing the transcript for a Bilibili video.
        """
        results = []

        metadata = {"video_urls": video_urls}

        for bili_url in video_urls:
            try:
                transcript = self.get_bilibili_info_and_subs(bili_url)
                results.append(DocumentNode(text=transcript, extra_info=metadata))
            except Exception as e:
                warnings.warn(
                    f"Error loading transcript for video {bili_url}: {str(e)}. Skipping video."
                )
        return results
