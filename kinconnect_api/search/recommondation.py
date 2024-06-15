from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_fireworks import FireworksEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_fireworks import FireworksEmbeddings
from dotenv import load_dotenv
from config import MONGO_CONNECTION_STRING, OPENAI_KEY


class Search:
    def __init__(self):
        load_dotenv()
        self.table = "kinconnect"
        self.collection = "profiles"

    def create_vector_search(self):
        """
        Creates a MongoDBAtlasVectorSearch object using the connection string, database, and collection names, along with the OpenAI embeddings and index configuration.

        :return: MongoDBAtlasVectorSearch object
        """
        vector_search = MongoDBAtlasVectorSearch.from_connection_string(
            MONGO_CONNECTION_STRING,
            "{}.{}".format(self.table, self.collection),
            FireworksEmbeddings(model="nomic-ai/nomic-embed-text-v1.5"),
            index_name="default"
        )
        return vector_search


    def perform_similarity_search(self, query, top_k=3):
        """
        This function performs a similarity search within a MongoDB Atlas collection. It leverages the capabilities of the MongoDB Atlas Search, which under the hood, may use the `$vectorSearch` operator, to find and return the top `k` documents that match the provided query semantically.

        :param query: The search query string.
        :param top_k: Number of top matches to return.
        :return: A list of the top `k` matching documents with their similarity scores.
        """

        # Get the MongoDBAtlasVectorSearch object
        vector_search = self.create_vector_search()

        # Execute the similarity search with the given query
        results = vector_search.similarity_search_with_score(
            query=query,
            k=top_k,
        )

        return results

if __name__ == "__main__":
    client = Search()
    print(client.perform_similarity_search("aaa"))



