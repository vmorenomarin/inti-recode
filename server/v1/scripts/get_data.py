# coding: utf-8
"""Author: Víctor Moreno Marín."""

# Pyhton libraries
from pymongo.mongo_client import MongoClient
from dotenv import dotenv_values

# Third party imports
# from articlemeta.client import RestfulClient
from journal_data import JournalData
from article_data import ArticleData

# Settings and instances
config = dotenv_values('.env')
journal_client = JournalData()
article_client = ArticleData()
mongo_client = MongoClient(host=config["MONGO_URI"])
db = mongo_client['scielo']

journal_client.save_collections()

collections = journal_client.collections_acrons()
def get_full_journals():
    """Get full journals collecion from SciELo database."""

    for acron in collections:
        journal_client.save_journals(acron)
        total_journals = db['journals'].count_documents()
    print(f'Journals collection in local database has {total_journals}')

if __name__ == "__main__":
    get_full_journals()        


    
