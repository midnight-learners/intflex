from typing import Self, Optional, List
from uuid import UUID, uuid4
from qdrant_client import QdrantClient
from qdrant_client.http.models import ScoredPoint
from qdrant_client.models import (
    PointStruct,
    VectorParams,
    Distance
)


class VecDBClient(QdrantClient):

    def __init__(self, collection_name: str, embedding_dim: int = 1536, *args, **kwargs) -> None:
        # Initialize super class
        super().__init__(*args, **kwargs)

        # # Create a new collection if it does not exist
        # if collection_name and collection_name not in self.collection_names:
        #     self.recreate_collection(
        #         collection_name=collection_name,
        #         vectors_config=VectorParams(
        #             size=embedding_dim,
        #             distance=Distance.COSINE
        #         )
        #     )
        #     print(f"Created collection <{collection_name}>")

        # Collection
        self._collection_name = collection_name
        self._embedding_dim = embedding_dim

    @property
    def collection_name(self) -> Optional[str]:
        return self._collection_name

    @property
    def collection_names(self) -> list[str]:
        return list(map(
            lambda collection: collection.name,
            self.get_collections().collections
        ))

    @classmethod
    def from_connection_string(cls, connection_string: str) -> Self:
        return cls(
            connection_string
        )

    def checkout_collection(self, collection_name: str) -> None:
        # Set the current collection name
        self._collection_name = collection_name

    def insert_vector(self, vec_id: str, vector: list[float], payload: dict) -> int:
        """
        Insert the embedding vector
        :param vec_id: 's id in vecdb
        :param vector: embedding vector
        :param payload: appending data
        :return: the number of inserted vectors
        """

        try:
            self.upsert(
                collection_name=self._collection_name,
                points=[
                    PointStruct(
                        id=vec_id,
                        vector=vector,
                        payload=payload
                    )
                ]
            )
            return 1
        except Exception as e:
            print(f"Error inserting vector: {e}")
            return 0

    def insert_vectors(self, to_vecdb_data: list[tuple[str, list[float], dict]]) -> int:
        """
        Insert the embedding vectors
        :param to_vecdb_data: format: [(vec_id, vector, payload), ...]
        :return: the number of inserted vectors
        """
        try:
            self.upsert(
                collection_name=self._collection_name,
                points=[
                    PointStruct(
                        id=vec_id,
                        vector=vector,
                        payload=payload
                    ) for vec_id, vector, payload in to_vecdb_data
                ]
            )
            return len(to_vecdb_data)
        except Exception as e:
            print(f"Error inserting vector: {e}")
            return 0

    def retrieve_similar_vectors(self, query_vec: list[float], top_k: int = 5) -> list[dict]:
        """
        Retrieve similar vectors
        :param query_vec: query vector
        :param top_k: number of similar vectors to retrieve
        :return: list of PointStruct Payload
        """
        # Find similar points
        points = self.search(
            collection_name=self._collection_name,
            query_vector=query_vec,
            limit=top_k,
            with_payload=True
        )

        return [point.payload for point in points if point.score >= 0.80]

    def retrieve_similar_note_vec_ids(self, query_vec: list[float], limit: int = 5) -> list[UUID]:
        # Find similar points
        points = self.search(
            collection_name=self._collection_name,
            query_vector=query_vec,
            limit=limit
        )

        # Vector IDs of similar notes
        vec_ids = list(map(
            lambda point: UUID(point.id),
            points
        ))

        return vec_ids

    def drop_collection(self) -> None:

        # Delete collection
        self.delete_collection(self._collection_name)

        # Recreate the collection
        self.recreate_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(
                size=self._embedding_dim,
                distance=Distance.COSINE
            )
        )


