# coding: utf-8
"""Author: Víctor Moreno Marín."""

# Pyhton libraries
# from pymongo.mongo_client import MongoClient
from dotenv import dotenv_values

# Third party imports
# from articlemeta.client import RestfulClient
from journal_data import JournalData
from article_data import ArticleData

# Settings and instances
# config = dotenv_values(".env")
journal_client = JournalData()
article_client = ArticleData()
# mongo_client = MongoClient(host=config["MONGO_URI"])
# db = mongo_client["scielo"]

save_collections = journal_client.get_collections()

# se debe crar un método en journals que constraste el número de coleccciones locale vs. el número de coleccione en Scielo. Este método debe ser invocado por get_collections.

