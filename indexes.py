
# Whoosh imports
from whoosh.fields import Schema, TEXT, NUMERIC, DATETIME, ID
from whoosh.index import create_in, open_dir
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import scoring

# MongoDB imports
from bson.objectid import ObjectId

# System imports
import os.path
import datetime

class QueryResults(object):
	""" Contains the query time and the documents that were returned. """

	def __init__(self, queryResult):

		self.documents = []
		""" The list of documents returned by the search. """
		for i in range(0, queryResult.scored_length()):
			doc = queryResult[i].fields()
			score = queryResult.score(i)
			self.documents.append({ 'score': score, 'document': doc })

		self.time = queryResult.runtime
		""" The total query time. This excludes mapping done by this code. """

class SchemaBuilder(object):
	""" Provides a way to build a normalized schema for any document type. """

	def build(self, document, size):
		""" Builds a schema based on the proeprties of a given document. """
		results = self.__build_normalized_base(document, size, True)

		self.__proccess_document(document, 0, results, self.__assign_value)

		return Schema(**results)

	def build_values(self, document, size):
		results = self.__build_normalized_base(document, size, False)

		def handler(name, value, container):
			container[name] = unicode(value)

		self.__proccess_document(document, 0, results, handler)
		return results

	def find_max_info(self, db):
		current = (0, None)
		for player in db.players.find():
			count = self.count_fields(player)
			if count > current[0]:
				current = (count, player)

		return current

	def __build_normalized_base(self, document, size, isForSchema):
		result = {}
		for index in range(1, size+1):
			if isForSchema:
				result[self.__make_prop_name(index)] = TEXT
			else:
				result[self.__make_prop_name(index)] = None
		
		return result

	def count_fields(self, document):
		count = 0
		for key, value in document.iteritems():
			valType = type(value)
			if(valType == dict):
				count += self.count_fields(value)
			else:
				count += 1
		return count

	def __proccess_document(self, document, index, results, handler):
		""" Process a given document and converts the properties to index properties. """

		for key, value in document.iteritems():
			valType = type(value)
			if(valType == dict):
				index = self.__proccess_document(value, index, results, handler)
			else:
				if value == None:
					# bad value, so assume string and set to unicode.
					value = u''

				index += 1
				actualName = self.__make_prop_name(index)
				handler(actualName, value, results)

		return index

	def __assign_value(self, name, value, structure):
		""" Maps a property name to a index type. """
		structure[name] = TEXT(analyzer=StemmingAnalyzer(), stored=True)

	def __make_prop_name(self, prop):
		""" Makes a property name in the format: prop1, prop2, prop3, etc. """

		if type(prop) is not int:
			raise ValueError("Parameter must be an integer value.")

		return "prop" + str(prop)


class IndexManager(object):
	def __init__(self, indexPath, indexSize, db):
		self.__index_path = indexPath
		self.__index_size = indexSize
		self.__db = db

	def build(self):
		""" Builds the index over all database items. """
		index = self.__get_index(self.__get_schema(), True)
		writer = index.writer()

		print "Indexing players..."
		self.__index_players(writer)
		print "Saving index..."

		print "Indexing restaruants..."
		self.__index_restaurants(writer)
		print "Saving index..."
		writer.commit()

		return index

	def search(self, text):
		""" Searches the index for anything containing the text. """

		schema = self.__get_schema()
		index = self.__get_index(schema, False)

		# Here we use TF-IDF because that is what our mongo search will use.
		with index.searcher(weighting=scoring.TF_IDF()) as searcher:
			query = MultifieldParser(schema.names(), schema=index.schema).parse(text)
			results = searcher.search(query)
			return QueryResults(results)

	def __get_index(self, full_schema, shouldClean):
		""" Creates an index if necessary and returns it. """

		if not os.path.exists(self.__index_path):
			os.mkdir(self.__index_path)
			return create_in(self.__index_path, full_schema)

		if shouldClean:
			create_in(self.__index_path, full_schema)

		return open_dir(self.__index_path)

	def __get_schema(self):
		# We use the player document because it contains the most fields.
		playerDoc = self.__db.players.find_one()
		builder = SchemaBuilder()
		return builder.build(playerDoc, self.__index_size)

	def __index_players(self, writer):
		""" Indexes the players collection. """
		builder = SchemaBuilder()

		total = self.__db.players.count()
		current = 0
		for player in self.__db.players.find({}):
			document = builder.build_values(player, self.__index_size)
			writer.add_document(**document)
			current += 1
			print "Players Indexed {0}/{1}".format(current, total)

	def __index_restaurants(self, writer):
		""" Indexes the restaraunts collection. """
		builder = SchemaBuilder()

		total = self.__db.restaurants.count()
		current = 0
		for rest in self.__db.restaurants.find({}):
			document = builder.build_values(rest, self.__index_size)
			writer.add_document(**document)
			current += 1
			print "Restaurants Indexed {0}/{1}".format(current, total)