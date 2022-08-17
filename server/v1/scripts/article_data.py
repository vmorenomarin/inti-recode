# coding: utf-8
"""Author: Víctor Moreno Marín."""

# Pyhton libraries
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
        # articles_per_journal = {}

        issn_list = []
        for journal in db["journals"].find({"collection": collection_acron}):
            issn_list.append(journal[code])

        for issn in issn_list:
            articles = scielo_client.documents(collection=collection_acron, issn=issn)
            for article in articles:
                if article:
                    db["articles"].insert_one(article.data)


# if __name__ == "__main__":
#     article_client = ArticleData()
#     oudated = JournalData()
#     articles = scielo_client.documents(collection="col", issn="0123-5923")
#     #     print(articles)
#     for article in articles:
#         print(type(article.data))
#         db["documents"].insert_one(article.data)
