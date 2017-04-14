
from lxml import etree, objectify
import requests

# Original search parameter methods from Slide 1 code samples.

class QueryBuilder(object):
	api_url = "https://en.wikipedia.org/w/api.php?"
	
	def withAction(self, whatAction):
		""" Builds an action query segment. """
		return 'action='+whatAction+'&'

	def withPageId(self, pageId):
		""" Builds an page query segment. """
		
		return 'pageid='+pageId+'&'

	def withFormat(self, whatFormat):
		""" Builds an return format query segment. """
		return 'format='+whatFormat+'&'

	def withLimitedSearch(self, searchTerms, limit):
		""" Builds an search terms and limit results query segments. """
		return 'search='+searchTerms+'&limit='+limit+'&'

	def withTitles(self, whatTitles):
		""" Builds an list of title query segments. """
		listOfTitles = ''
		for title in whatTitles:
			listOfTitles += title+"|"
		return 'titles=' + listOfTitles[:-1] + '&'

	def withProperty(self, property):
		""" Builds a prop query segment. """
		return 'prop=' + property + '&'

	def withTitle(self, title):
		""" Builds a title query segment. """
		return 'page=' + title + '&'

	def withSection(self, sectionId):
		""" Builds a section query segment. """
		return 'section=' + sectionId + '&'

	def buildSearchUrl(self, searchTerms, limit):
		""" Builds a fully qualified search query url using opensearch and xml response. """
		return self.api_url + self.withAction('opensearch') + self.withFormat('xml') + self.withLimitedSearch(searchTerms, limit)

	def buildQueryUrl(self, queryTerms):
		""" Builds a fully qualified query url using an xml response. """
		return self.api_url + self.withAction('query') + self.withFormat('xml') + self.withTitles(queryTerms)
		
	def buildPageDetailsUrl(self, pageid, property):
		""" Builds a fully qualified url for getting a page details. Property is used to define what is returned."""
		return self.api_url + self.withAction('parse') + \
			self.withFormat('xml') + \
			self.withPageId(pageid) + \
			self.withProperty(property)

	def buildPageDetailsFromTitleUrl(self, title, property):
		""" Builds a fully qualified url for getting a page details. Property is used to define what is returned."""
		return self.api_url + self.withAction('parse') + \
			self.withFormat('xml') + \
			self.withTitle(title) + \
			self.withProperty(property)

	def buildSectionUrl(self, pageid, sectionId, property):
		""" Builds a fully qualified url for section a page. Property is used to define what is returned. """
		return self.api_url + self.withAction('parse') + \
			self.withFormat('xml') + \
			self.withPageId(pageid) + \
			self.withSection(sectionId)

class BaseCrawler(object):
	""" Provides base methods for all crawler type objects. """

	""" The query builder to use for requests. """
	builder = QueryBuilder()

	def __strip_ns__(self, tree):
		""" Strips any namespace formatting off of tags. """
		for node in tree.iter():
			try:
				has_namespace = node.tag.startswith('{')
			except AttributeError:
				continue
			if has_namespace:
				node.tag = node.tag.split('}', 1)[1]

	def beautify(self, e):
		""" Prints a nicely formatted version of the given tree object. """
		print etree.tostring(e, pretty_print=True)
		print ''

	def __getRequest__(self, url):
		""" Performs a GET request using the provided url. """
		pageResponse = requests.get(url)
		# Now normalize the response
		tree = etree.fromstring(pageResponse.content)
		self.__strip_ns__(tree)
		return tree

class NFLCrawler(BaseCrawler):
	""" Base crawler for obtaining all the details of the NFL main page. """

	""" The id of the NFL page. This will be queried, but -1 tells it to query. """
	nfl_page_id = -1

	def __getNFLPageId__(self):
		""" Gets and sets the id of the NFL landing page. """
		if self.nfl_page_id != -1:
			return self.nfl_page_id

		# Build the search
		search = self.builder.buildQueryUrl(["National Football League"])

		# Do the GET request
		root = self.__getRequest__(search)

		# Find the page id
		pageids = root.xpath('/api/query/pages/page/@pageid')

		# Set the id and return.
		self.nfl_page_id = pageids[0]
		return self.nfl_page_id

	def getNFLHtmlContent(self):
		""" Gets the HTML content for the main NFL page. """

		if self.nfl_page_id == -1:
			self.__getNFLPageId__()

		# Get details URL.
		url = self.builder.buildPageDetailsUrl(self.nfl_page_id, 'sections')

		# Return the normalized response.
		return self.__getRequest__(url)


	def getClubsSectionIndex(self):
		""" Gets the section of the main NFL page containing the clubs list. """

		# Get all the sections
		sections = self.getNFLHtmlContent()
		nodes = sections.xpath('/api/parse/sections/s')

		# Find the section named Clubs.
		for node in nodes:
			if node.get('line') != 'Clubs':
				continue

			# Return the id of the clubs section.
			return node.get('index')

	def getClubsHtml(self):
		""" Gets the HTML for the clubs section. """

		# Get the clubs index
		clubSection = self.getClubsSectionIndex()

		# Build the url for the HTML body of the section.
		url = self.builder.buildSectionUrl(self.nfl_page_id, clubSection, 'text')
		
		# Get the response
		nodes = self.__getRequest__(url)

		# Extract only the HTML string
		html = nodes.xpath('/api/parse/text/text()')

		# Find the table that has the teams listed. 
		tables = etree.HTML(html[0]).xpath('//table[@class="navbox plainrowheaders wikitable"]')
		return tables[0]