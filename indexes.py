
from whoosh.fields import Schema, TEXT, NUMERIC, DATETIME, ID
from whoosh.index import create_in, open_dir
from whoosh.analysis import StemmingAnalyzer

from bson.objectid import ObjectId

import os.path
import datetime

class SchemaBuilder(object):
	""" Provides a way to build a normalized schema for any document type. """

	def build(self, document):
		""" Builds a schema based on the proeprties of a given document. """
		results = {}

		self.__proccess_document(document, 0, results, self.__assign_value)

		return Schema(**results)

	def build_values(self, document):
		results = {}

		def handler(name, value, container):
			container[name] = value

		self.__proccess_document(document, 0, results, handler)
		return results

	def __proccess_document(self, document, index, results, handler):
		""" Process a given document and converts the properties to index properties. """

		for key, value in document.iteritems():
			valType = type(value)
			if(valType == dict):
				index = self.__proccess_document(value, index, results, handler)
			else:
				index += 1
				actualName = self.__make_prop_name(index)
				handler(actualName, value, results)

				# if insertingVals:
				# 	# building document to add, so do that instead.
				# 	results[actualName] = value
				# else:
				# 	# Building the schema only, so process the index type
				# 	self.__assign_value(index, key, results)
		return index

	def __assign_value(self, name, value, structure):
		""" Maps a property name to a index type. """

		propType = type(value)

		if propType == int:
			# Do integer index type
			structure[name] = NUMERIC
		elif propType == unicode or propType == str:
			# Do text type
			structure[name] = TEXT(analyzer=StemmingAnalyzer())
		elif propType == datetime.datetime or propType == datetime.date:
			# Do date type
			structure[name] = DATETIME
		elif isinstance(value, ObjectId):
			# ID Value
			structure[name] = ID(stored=True)
		elif propType == type(None):
			return
		else:
			print propType
			print value
			print type(ObjectId)
			# Not anything, so throw
			raise ValueError("Invaild property value for index.")

	def __make_prop_name(self, prop):
		""" Makes a property name in the format: prop1, prop2, prop3, etc. """

		if type(prop) is not int:
			raise ValueError("Parameter must be an integer value.")

		return "prop" + str(prop)


class IndexBuilder(object):
	def __init__(self, indexPath):
		self.__index_path = indexPath

	def __get_index(self, full_schema):
		""" Creates an index if necessary and returns it. """

		if not os.path.exists(self.__index_path):
			os.mkdir(self.__index_path)
		ix = create_in(self.__index_path, full_schema)
		return open_dir(self.__index_path)

	def build(self, db):
		""" Builds the index over all database items. """
		index = self.__get_index(self.__get_schema(db))
		writer = index.writer()
		self.__index_players(writer, db)

	def __get_schema(self, db):
		# We use the player document because it contains the most fields.
		playerDoc = db.players.find_one()

		builder = SchemaBuilder()
		return builder(playerDoc)

	def __index_players(self, writer, db):
		""" Indexes the players collection. """

		for player in db.players.find({}):
			writer.add_document()