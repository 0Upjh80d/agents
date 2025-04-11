import warnings

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.results import InsertOneResult

warnings.filterwarnings(
    "ignore", message="You appear to be connected to a CosmosDB cluster"
)


class PyMongoCosmosDBClient:
    def __init__(self, *, database_id: str, collection_id: str, connection_string: str):
        self.database_id = database_id
        self.collection_id = collection_id
        self.connection_string = connection_string
        self._collection = None  # cache collection reference
        self._client = None  # cache client

    async def _get_client(self) -> AsyncIOMotorClient:
        """
        Gets the client to manage the database and collection. The client is cached as a private attribute.

        Returns:
            AsyncIOMotorClient: The client.
        """
        if self._client is None:
            self._client = AsyncIOMotorClient(self.connection_string)
        return self._client

    async def _get_collection(self) -> AsyncCollection:
        """
        Gets the collection to connect to and perform operations. The collection is cached as a private attribute.

        Returns:
            AsyncCollection: The collection.

        Raises:
            ValueError: Raise ValueError if database or collection does not exist.
        """
        if self._collection is None:

            client = await self._get_client()
            db = client[self.database_id]

            database_names = await client.list_database_names()
            if self.database_id not in database_names:
                raise ValueError(
                    f"Database does not exist. Please ensure the {self.database_id} database has been created."
                )

            collection_names = await db.list_collection_names()
            if self.collection_id not in collection_names:
                raise ValueError(
                    f"Collection does not exist. Please ensure the {self.collection_id} collection has been created."
                )

            self._collection = db.get_collection(self.collection_id)

        return self._collection

    async def _insert_document(
        self, data: BaseModel, collection: AsyncCollection
    ) -> InsertOneResult:
        """
        Creates a document.

        Args:
            data (BaseModel): The Pydantic base model.
            collection (AsyncCollection): The collection to insert the document to.

        Returns:
            InsertOneResult: The `InsertOneResult` object.
        """
        result = await collection.insert_one(data.model_dump())
        return result

    async def _find_documents(
        self, collection: AsyncCollection, *, query_dict: dict[str, str]
    ) -> list[dict]:
        """
        Retrieves documents from the collection that match the search criteria.

        Args:
            collection (AsyncCollection): The collection to search in.
            query_dict (dict[str,str]): The dictionary containing the search criteria.

        Returns:
            list[dict]: A list of documents (dictonaries) that match the search criteria.
        """
        result = collection.find(query_dict)
        documents = [doc async for doc in result]
        return documents

    async def _upsert_document(
        self,
        data: BaseModel,
        collection: AsyncCollection,
        *,
        query_dict: dict[str, str],
    ) -> dict:
        """
        Upserts a document based on the search criteria.

        Args:
            data (BaseModel): The Pydantic base model.
            collection (AsyncCollection): The collection to upsert the document to.
            query_dict (dict[str]): The dict to search against to update the document(s), if it or they exist(s); otherwise insert.

        Returns:
            dict: A dictionary containing the raw results.
        """
        result = await collection.update_one(
            query_dict, {"$set": data.model_dump()}, upsert=True
        )
        return result.raw_result

    async def _delete_document(
        self, collection: AsyncCollection, *, query_dict: dict[str, str]
    ) -> dict:
        """
        Deletes a documents from the collection that match the search criteria..

        Args:
            collection (AsyncCollection): The collection to delete the document from.
            query_dict (dict[str,str]): The dictionary containing the search criteria.

        Returns:
            dict: A dictionary containing the raw results.
        """
        result = await collection.delete_one(query_dict)
        return result.raw_result

    async def _upsert_all_documents_fields(
        self,
        fields: dict[str, any],
        collection: AsyncCollection,
        *,
        query_dict: dict[str, str],
    ) -> dict:
        """
        Upserts (updates or inserts) a field in all documents that match the search criteria.

        Args:
            data (dict[str, any]): The dictionary containing fields to update.
            collection (AsyncCollection): The collection to upsert the documents in.
            query_dict (dict[str, str]): The dictionary containing the search criteria.

        Returns:
            dict: A dictionary containing the raw results.
        """
        result = await collection.update_many(query_dict, {"$set": fields}, upsert=True)
        return result.raw_result

    async def get_collection_and_upsert_all_documents_fields(
        self, fields: dict[str, any], *, query_dict: dict[str, str]
    ) -> dict:
        """
        Gets the collection, and performs an UPDATE operation on all matching documents.

        Args:
            fields (dict[str, any]): The dictionary containing fields to update.
            query_dict (dict[str, str]): The dictionary containing the search criteria.

        Returns:
            dict: A dictionary containing the raw results.
        """
        collection = await self._get_collection()
        raw_result = await self._upsert_all_documents_fields(
            fields, collection, query_dict=query_dict
        )
        return raw_result

    async def get_collection_and_insert_to_collection(
        self, data: BaseModel
    ) -> InsertOneResult:
        """
        Gets the collection and performs CREATE operation.

        Args:
            data (BaseModel): The Pydantic base model.

        Returns:
            InsertOneResult: The `InsertOneResult` object.
        """
        collection = await self._get_collection()
        result = await self._insert_document(data, collection)
        return result

    async def get_collection_and_find_documents(
        self, *, query_dict: dict[str, str]
    ) -> list[dict]:
        """
        Gets the collection and performs RETRIEVE operation.

        Args:
            query_dict (dict[str,str]): The dictionary containing the search criteria.

        Returns:
            list[dict]: A list of documents (dictonaries) that match the search criteria.
        """
        collection = await self._get_collection()
        documents = await self._find_documents(collection, query_dict=query_dict)
        return documents

    async def get_collection_and_upsert_document(
        self, data: BaseModel, *, query_dict: dict[str, str]
    ) -> dict:
        """
        Gets the collection and performs either an UPDATE or CREATE operation.

        Args:
            data (BaseModel): The Pydantic base model.
            query_dict (dict[str,str]): The dictionary containing the search criteria.

        Returns:
            dict: A dictionary containing the raw results.
        """
        collection = await self._get_collection()
        raw_result = await self._upsert_document(
            data, collection, query_dict=query_dict
        )
        return raw_result

    async def get_collection_and_delete_document(
        self, *, query_dict: dict[str, str]
    ) -> dict:
        """
        Gets the collection and performs either a DELETE operation.

        Args:
            query_dict (dict[str,str]): The dictionary containing the search criteria.

        Returns:
            dict: A dictionary containing the raw results.
        """
        collection = await self._get_collection()
        raw_result = await self._delete_document(collection, query_dict)
        return raw_result
