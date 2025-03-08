from abc import ABC, abstractmethod


class BaseResponder(ABC):
    @abstractmethod
    def generate_response(self, query: str, retrieved_documents: list[dict]) -> str:
        """
        Generate a final answer given the query and a list of retrieved documents.
        """
