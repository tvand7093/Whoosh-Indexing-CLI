from os.path import join, dirname
from dotenv import load_dotenv
from pymongo import MongoClient

import os
import urllib

class Settings(object):
    """ Represents the .env settings and database connection. """
    
    def __init__(self):
        # Load up the environment variables
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        self.__set_props()

    def __set_props(self):
        """ Sets the settings from the .env file.""" 

        self.mongo_user = os.environ.get("MONGO_USER")
        """ The mongodb username to use. """

        self.mongo_pass = os.environ.get("MONGO_PASS")
        """ The mongodb password to use. """

        self.mongo_host = os.environ.get("MONGO_HOST")
        """ The url host name (and port) of the remote/local database."""

        self.mongo_database = os.environ.get("MONGO_DB")
        """ The database to connect to. """

        mongoUrl = self.__db_url()

        self.db = MongoClient(host=self.__db_url())[self.mongo_database]
        """ The MongoClient database instance."""

    def __db_url(self):
        """ Formats the properties into a mongodb url."""

        password = urllib.quote_plus(self.mongo_pass)
        return "mongodb://{0}:{1}@{2}/{3}".format(self.mongo_user, 
            password,
            self.mongo_host,
            self.mongo_database)