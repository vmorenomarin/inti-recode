# coding: utf-8
"""Author: Víctor Moreno Marín."""

# Pyhton libraries
from re import T
import requests
from pymongo.mongo_client import MongoClient
from dotenv import dotenv_values

# Third party imports
from articlemeta.client import RestfulClient
from journal_data import JournalData

# Settings and instances
config = dotenv_values(".env")
scielo_client = RestfulClient()
journal_client = JournalData()
# mongo_client = MongoClient(host=config["HOST"], port=int(config["PORT"]))
mongo_client = MongoClient(host=config["MONGO_URI"])
db = mongo_client["scielo"]


class ArticleData:
    """Methods for retieve article metadata from Scielo usign official API.

    Methods:
            get_articles(): Retrieve articles from Scielo for a journal.
    -------
    """

    def get_articles(self, code: str, collection_acron: str) -> None:
        """Retrieve articles from Scielo for a journal.

        Arguments:
                code (str): ISSN code of journal to get the article metadata.
                collection (str): Collection name acronym from belong journal.

        Returns:
                None

        """
        articles_per_journal = {}

        issn_list = []
        for journal in db["journals"].find({"collection": collection_acron}):
            issn_list.append(journal[code])


if __name__ == "__main__":
    article_client = ArticleData()
    oudated = JournalData()
    articles = scielo_client.documents(collection="ecu", issn="0120-4874", body=True)
    counter = 0
