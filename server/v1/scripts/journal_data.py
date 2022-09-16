# coding: utf-8
"""Author: Víctor Moreno Marín."""

# Pyhton libraries
from ast import Pass
import requests
from pymongo.mongo_client import MongoClient
from dotenv import dotenv_values

# Third party imports
from articlemeta.client import RestfulClient

# Settings and instances
config = dotenv_values(".env")
scielo_client = RestfulClient()
# mongo_client = MongoClient(host=config['HOST'], port=int(config['PORT']))
mongo_client = MongoClient(host=config["MONGO_URI"])
db = mongo_client["scielo"]


class JournalData:
    """
    Methods for retieve specific jorunal metadata from Scielo using official data.

    Methods
    -------
    collections_checker():
        Verify for new collections in Scielo.

    save_collections():
        Save collections from Scielo in a Mongo DB collection.

    get_collections():
        Return acron and original names collections from Scielo DB.

    get_articles_by_collection():
        Return and save in the Mongo data base.

    save_journals():
        Return and save journal metadata in the Mongo data base.

    journals_checker():
        Check number of journals in local database and compare with Scielo DB.

    compare_date():
        Compare dates in journals from a collection.

    update_journals():
        Update journals in collection.
    """

    URL = scielo_client.ARTICLEMETA_URL
    JOURNAL_ENDPOINT = scielo_client.JOURNAL_ENDPOINT
    LIMIT = 1000

    def collections_checker(self) -> bool:
        """Verify for new collections in SciELo."""
        number_local_collections = db["collections"].count_documents({})
        number_scielo_collections = len(scielo_client.collections())
        return number_local_collections == number_scielo_collections

    def save_collections(self) -> None:
        """Save collections from SciELo in a Mongo DB collection."""
        if not self.collections_checker():
            for collection in scielo_client.collections():
                db["collections"].insert_one(collection)
                counter = db["collections"].count_documents({})
        print(f"Collection data is updated with {counter} journals.")

    def get_collections(self) -> dict:
        """Return acronyms and original names of the collections from SciELo DB."""
        collection_names = {}
        for collection in scielo_client.collections():
            collection_names.update({collection["original_name"]: collection["acron"]})
        return collection_names

    def collections_acrons(self) -> list:
        """Return only acronyms of the collections from local DB.

        Use this method only with local saved collections.
        """
        collections = self.get_collections()
        collections_acrons = list(collections.values())
        return collections_acrons

    def journals_checker(self, collection_acron: str) -> tuple:
        """
        Check number of journals in local database and compare with Scielo DB.

        If number of journals for a collection in local database is equal to SciElo journals database in same collection, the method returns true
        and number difference in journals.

        Parameters:
                collection_acron (str): Acronym in three letters for collection.

        Returns:
                (Tuple): Tuple with a boolean value and integer value.
        """
        number_local_journals = db["journals"].count_documents({})
        response = requests.get(
            self.URL + self.JOURNAL_ENDPOINT + "/identifiers",
            {"collection": collection_acron},
        )
        response = response.json()
        number_scielo_journals = response["meta"]["total"]
        if number_local_journals == number_scielo_journals:
            return (True, 0)
        difference = number_scielo_journals - number_local_journals

        return (False, difference)

    def compare_date(self, collection_acron: str) -> dict:
        """
        Compare dates in journals from a collection.

        This function compares the field 'processing_date'. When field are different
        from SciElo database, the function returns a dictionary with issn codes
        of journals to update.

        Returns:
                (dict): Returns a dictrionary with issn of journals with
                        different 'processing_date' in a collection.
        """
        response = requests.get(
            self.URL + self.JOURNAL_ENDPOINT + "/identifiers",
            {"collection": collection_acron},
        ).json()
        remote_journals = response["objects"]
        outdated_journals = {}
        issn_list = []
        if not self.journals_checker(collection_acron)[0]:
            return self.update_journals(collection_acron)
        for journal in remote_journals:
            local_journal = db["journals"].find_one(
                {"collection": collection_acron, "code": journal["code"]}
            )

            if local_journal["processing_date"] != journal["processing_date"]:
                issn_list.append(journal["code"])
            outdated_journals.update({collection_acron: issn_list})

        return outdated_journals

    def update_journals(self, collection_acron: str) -> int:
        """
        Update journals in collection.

        This function compares local journals number with Scielo journals for same collection.
        Retrieves data for new journal and insert it into local data base.

        Parameters:
                collection_acro (str): Acronym in three letters for collection

        Returns:
                (int): Returns number of modified journals.
        """
        checker = self.journals_checker(
            collection_acron
        )  # Get tuple values as return of this method.
        if not checker[0]:
            # Retrive code from Scielo to compare with local
            response = requests.get(
                self.URL + self.JOURNAL_ENDPOINT + "/identifiers",
                {"collection": collection_acron},
            ).json()

            journals_difference = checker[1]
            print(f"{journals_difference} to retrieve.")
            codes = [
                journal["code"]
                for journal in response["objects"][-journals_difference:]
            ]  # ISSN codes list.

            for code in codes:
                new_journal = scielo_client.journal(
                    code=code, collection=collection_acron
                )
                db["journals"].insert_one(new_journal.data)

        journals_to_update = self.compare_date(collection_acron)
        count_modifications = 0
        if journals_to_update:

            for journal_code in journals_to_update[collection_acron]:
                response = requests.get(
                    self.URL + self.JOURNAL_ENDPOINT,
                    {"collection": collection_acron, "code": journal_code},
                ).json()
                new_journal_data = response[0]
                result = db["journals"].replace_one(
                    {"code": journal_code}, new_journal_data
                )
                count_modifications += result.modified_count

        return count_modifications

    def save_journals(self, collection_acron: str) -> None:
        """Save journal metadata in the Mongo data base.

        Parameters:
                colection_acron (str): Acronym in three letters for collection.
        """
        journals = scielo_client.journals(collection_acron)
        try:
            if not self.journals_checker(collection_acron)[0]:
                db["collections"].delete_many({"collection": collection_acron})

                print(
                    f"Getting collections for collection with {collection_acron} code..."
                )
                response = requests.get(
                    self.JOURNAL_ENDPOINT + "/identifiers", params=collection_acron
                ).json()
                total_journals = response["meta"][
                    "total"
                ]  # Get total of journals in collection.

                if total_journals < self.LIMIT:
                    for journal in journals:
                        db["journals"].insert_one(journal.data)
                else:
                    # request_counter = 0
                    for journal, request_counter in zip(journals, range(self.LIMIT)):
                        pass

                partial_count = db["journals"].count_documents({})
                print("Journal collections was added in your local database.")
                print(
                    f"Downloaded jounals {partial_count} for collection with {collection_acron} code."
                )
        except Exception:
            Exception


# if __name__ == "__main__":
#     journal_client = JournalData()
#     oudated = journal_client.get_collections()
#     print(list(oudated.values()))
