# This file has been modified by the Nextpy Team in 2023 using AI tools and automation scripts. 
# We have rigorously tested these modifications to ensure reliability and performance. Based on successful test results, we are confident in the quality and stability of these changes.

"""SingleStore reader."""

from typing import List

from nextpy.ai import download_loader
from nextpy.ai.rag.document_loaders.basereader import BaseReader
from nextpy.ai.schema import DocumentNode


class SingleStoreReader(BaseReader):
    """SingleStore reader.

    Args:
        scheme (str): Database Scheme.
        host (str): Database Host.
        port (str): Database Port.
        user (str): Database User.
        password (str): Database Password.
        dbname (str): Database Name.
        table_name (str): Table Name.
        content_field (str): Content Field.
        vector_field (str): Vector Field.
    """

    def __init__(
        self,
        scheme: str,
        host: str,
        port: str,
        user: str,
        password: str,
        dbname: str,
        table_name: str,
        content_field: str = "text",
        vector_field: str = "embedding",
    ):
        """Initialize with parameters."""
        self.scheme = scheme
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.table_name = table_name
        self.content_field = content_field
        self.vector_field = vector_field

        try:
            import pymysql

            pymysql.install_as_MySQLdb()
        except ImportError:
            pass

        try:
            from nextpy.ai.rag.document_loaders.utils import import_loader

            self.DatabaseReader = import_loader("DatabaseReader")
        except:
            self.DatabaseReader = download_loader("DatabaseReader")

        self.reader = self.DatabaseReader(
            scheme=self.scheme,
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.dbname,
        )

    def load_data(self, search_embedding: str, top_k: int = 5) -> List[DocumentNode]:
        """Load data from SingleStore.

        Args:
            search_embedding (str): The embedding to search.
            top_k (int): Number of results to return.

        Returns:
            List[DocumentNode]: A list of documents.
        """
        query = f"""
        SELECT {self.content_field}, DOT_PRODUCT_F64({self.vector_field}, JSON_ARRAY_PACK_F64(\'{search_embedding}\')) AS score 
        FROM {self.table_name} 
        ORDER BY score 
        DESC LIMIT {top_k}
        """

        return self.reader.load_data(query=query)
