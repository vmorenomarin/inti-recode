"""Using scielo api."""

# Pyhton libraries
from http import client
from logging import log
from pprint import pprint
import requests
from pymongo.mongo_client import MongoClient
from dotenv import dotenv_values

# Third party imports
from articlemeta.client import RestfulClient


# Settings and instances
config = dotenv_values(".env")
scielo_client = RestfulClient()

URL = scielo_client.ARTICLEMETA_URL
journal_endpoint = scielo_client.JOURNAL_ENDPOINT

# mongo_client = MongoClient(host=config["HOST"], port=int(config["PORT"]))
mongo_client = MongoClient(host=config["MONGO_URI"])

db = mongo_client["scielo"]


class DataScielo:
    """
    Methods to get specific data from Scielo.

    Methods
    -------
    code_colecctions():
        Return acron and original names collections from Scielo DB.

    get_articles_by_collection():
        Return and save in the Mongo data base.

    get_save_journals_in_collection():
        Return and save journal metadata in the Mongo data base.

    journals_in_collection_checker(self, collection_acron: str):
        Check number of journals in local database and compare with Scielo DB.
    """

    def code_collections(self):
        """Return acrons and original names of the collections from Scielo DB."""
        collection_acrons = []
        for collection in scielo_client.collections():
            collection_acrons.append({collection["original_name"]: collection["acron"]})
        return collection_acrons

    def get_collections(self):
        """Save collections from Scielo in a Mongo DB collection."""
        for collection in scielo_client.collections():
            db["collections"].insert_one(collection)
        # return collection_acrons

    def get_save_journals_in_collection(self, collection_acron: str):
        """
        Return and save journal metadata in the Mongo data base.

        Parameters:
                colection_acron (str): Acronym in three letters for collection
        """
        journals = scielo_client.journals(
            collection_acron
        )  # Journals is a generator object.
        try:
            for journal in journals:
                db["journals"].insert_one(journal.data)
        except Exception as e:
            log(e)

    def journals_in_collection_checker(self, collection_acron: str):
        """
        Check number of journals in local database and compare with Scielo DB.

        Parameters:
                collection_acron (str): Acronym in three letters for collection

        Returns:
                (bool): Booolean validation
        """
        number_journals_local = db["journals"].count_documents({})
        response = requests.get(
            URL + journal_endpoint + "/identifiers", {"collection": collection_acron}
        )
        response = response.json()
        number_journals_scielo = response["meta"]["total"]

        return number_journals_local == number_journals_scielo

    def update_journals(self, collection_acron):
        """
        Update journals in a collection.

        This function compares local collectiosn number with Scielo journals for same collection.
        Retrieve data for new journal and insert into local data base.

        Parameters:
                collection_acro (str): Acronym in three letters for collection
        """
        if self.journals_in_collection_checker(collection_acron):
            pass


# client= DataScielo()
# # returned = client.journals_in_collection_checker("col")
# print(returned)
