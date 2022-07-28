# coding: utf-8
"""Author: Víctor Moreno Marín."""

# Pyhton libraries
from itertools import count
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
# mongo_client = MongoClient(host=config["HOST"], port=int(config["PORT"]))
mongo_client = MongoClient(host=config["MONGO_URI"])
db = mongo_client["scielo"]

URL = scielo_client.ARTICLEMETA_URL
JOURNAL_ENDPOINT = scielo_client.JOURNAL_ENDPOINT


class DataScielo:
    """
    Methods to get specific data from Scielo.

    Methods
    -------
    code_collections():
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
        number_local_journals = db["journals"].count_documents({})
        response = requests.get(
            URL + JOURNAL_ENDPOINT + "/identifiers", {"collection": collection_acron}
        )
        response = response.json()
        number_scielo_journals = response["meta"]["total"]

        return number_local_journals == number_scielo_journals

    def compare_date(self, collection_acron: str) -> dict:
        """
        Compare dates in journals from a collection.

        This function compares the field "processing_date". When field are different from SciElo database, the function returns a dictionary with issn codess of journals to update.

        Returns:
                (dict): Returns a dictrionary with issn of journals with different "processing_date" in a collection.
        """
        response = requests.get(
            URL + JOURNAL_ENDPOINT + "/identifiers", {"collection": collection_acron}
        )
        response = response.json()
        remote_journals = response["objects"]
        outdated_journals = {}
        issn_list = []
        for journal in remote_journals:
            local_journal = db["journals"].find_one(
                {"collection": collection_acron, "code": journal["code"]}
            )
            if local_journal["processing_date"] != journal["processing_date"]:
                issn_list.append(journal["code"])
            outdated_journals.update({collection_acron: issn_list})
        return outdated_journals

    def update_journals(self, collection_acron: str) -> int :
        """
        Update journals in collection.

        This function compares local collectiosn number with Scielo journals for same collection.
        Retrieve data for new journal and insert into local data base.

        Parameters:
                collection_acro (str): Acronym in three letters for collection

        Returns:
                (int): Returns number of modified journals.
        """
        if not self.journals_in_collection_checker(collection_acron):
            pass

        journals_to_update = self.compare_date(collection_acron)
        if journals_to_update:
            count_modifications = 0
            for journal_code in journals_to_update[collection_acron]:
                response = requests.get(
                    URL + JOURNAL_ENDPOINT,
                    {"collection": collection_acron, "code": journal_code},
                )
                new_journal_data = response.json()[0]
                result = db["journals"].replace_one(
                    {"code": journal_code}, new_journal_data
                )
                count_modifications += 1
        return count_modifications


# client= DataScielo();
# returned = client.journals_in_collection_checker("col");
# print(returned);
