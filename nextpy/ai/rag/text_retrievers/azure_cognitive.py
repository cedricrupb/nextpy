# This file has been modified by the Nextpy Team in 2023 using AI tools and automation scripts. 
# We have rigorously tested these modifications to ensure reliability and performance. Based on successful test results, we are confident in the quality and stability of these changes.

"""Retriever wrapper for Azure Cognitive Search."""
from __future__ import annotations

import json
from typing import Dict, List, Optional

import aiohttp
import requests
from pydantic import BaseModel, Extra, root_validator

from nextpy.ai.schema import BaseRetriever, Document
from nextpy.utils.data_ops import get_from_dict_or_env


class AzureCognitiveSearchRetriever(BaseRetriever, BaseModel):
    """Wrapper around Azure Cognitive Search."""

    service_name: str = ""
    """Name of Azure Cognitive Search service"""
    index_name: str = ""
    """Name of Index inside Azure Cognitive Search service"""
    api_key: str = ""
    """API Key. Both Admin and Query keys work, but for reading data it's
    recommended to use a Query key."""
    api_version: str = "2020-06-30"
    """API version"""
    aiosession: Optional[aiohttp.ClientSession] = None
    """ClientSession, in case we want to reuse connection for better performance."""
    content_key: str = "content"
    """Key in a retrieved result to set as the Document page_content."""

    class Config:
        extra = Extra.forbid
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that service name, index name and api key exists in environment."""
        values["service_name"] = get_from_dict_or_env(
            values, "service_name", "AZURE_COGNITIVE_SEARCH_SERVICE_NAME"
        )
        values["index_name"] = get_from_dict_or_env(
            values, "index_name", "AZURE_COGNITIVE_SEARCH_INDEX_NAME"
        )
        values["api_key"] = get_from_dict_or_env(
            values, "api_key", "AZURE_COGNITIVE_SEARCH_API_KEY"
        )
        return values

    def _build_search_url(self, query: str) -> str:
        base_url = f"https://{self.service_name}.search.windows.net/"
        endpoint_path = f"indexes/{self.index_name}/docs?api-version={self.api_version}"
        return base_url + endpoint_path + f"&search={query}"

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }

    def _search(self, query: str) -> List[dict]:
        search_url = self._build_search_url(query)
        response = requests.get(search_url, headers=self._headers)
        if response.status_code != 200:
            raise Exception(f"Error in search request: {response}")

        return json.loads(response.text)["value"]

    async def _asearch(self, query: str) -> List[dict]:
        search_url = self._build_search_url(query)
        if not self.aiosession:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=self._headers) as response:
                    response_json = await response.json()
        else:
            async with self.aiosession.get(
                search_url, headers=self._headers
            ) as response:
                response_json = await response.json()

        return response_json["value"]

    def get_relevant_documents(self, query: str) -> List[Document]:
        search_results = self._search(query)

        return [
            Document(page_content=result.pop(self.content_key), metadata=result)
            for result in search_results
        ]

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        search_results = await self._asearch(query)

        return [
            Document(page_content=result.pop(self.content_key), metadata=result)
            for result in search_results
        ]
