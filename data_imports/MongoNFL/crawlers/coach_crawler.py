from nfl_crawler import BaseCrawler
from lxml import etree, objectify

class CoachCrawler(BaseCrawler):
    """ Provides access to the HTML table containing coach data. """
    
    def getDetailsTable(self, subUrl):
        splitUrl = subUrl.split('/')
        pageId = splitUrl[len(splitUrl) - 1]
        query = self.builder.buildPageDetailsFromTitleUrl(pageId, 'text')
        tree = self.__getRequest__(query)
        html = tree.xpath('/api/parse/text/text()')
        # Find the table that has the teams listed. 
        return etree.HTML(html[0]).xpath('//table[@class="infobox vcard"]')[0]