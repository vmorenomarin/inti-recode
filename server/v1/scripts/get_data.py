"""Using scielo api."""

# Pyhton libraries
from pprint import pprint
from pymongo.mongo_client import MongoClient
from dotenv import dotenv_values

# Third party imports
from articlemeta.client import RestfulClient

# Settings and instances
config = dotenv_values(".env")
scielo_client = RestfulClient()
mongo_client = MongoClient(host=config["HOST"], port=int(config["PORT"]))

db = mongo_client["scielo"]


class DataScielo:
    """Methods to get specific data from Scielo.

    Methods
    -------
    code_colecctions():
        Return acron and original names collections from Scielo DB.

    get_articles_by_collection():
        Return and save in the Mongo data base.

    get_save_journals_in_collection():
        Return and save journal metadata in the Mongo data base.
    """

    def code_collections(self):
        """Return acrons and original names of the collections from Scielo DB."""
        collection_acrons = []
        for collection in scielo_client.collections():
            collection_acrons.append(
                {collection["original_name"]: collection["acron"]})
        return collection_acrons

    def get_collections(self):
        """Save collections from Scielo in a Mongo DB collection."""
        for collection in scielo_client.collections():
            db["collections"].insert_one(collection)
        # return collection_acrons

    def get_save_journals_in_collection(self, collection_acron):
        """Return and save journal metadata in the Mongo data base.

        Parameters:
        colection_acron: String
        """
        journals = scielo_client.journals(
            collection_acron)  # Journals is a generator object.
        for journal in journals:
            db["journals"].insert_one(journal.data)

# client=DataScielo()
# client.get_save_journals_in_collection("col")
