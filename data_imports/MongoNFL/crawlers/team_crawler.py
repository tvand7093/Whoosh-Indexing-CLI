from nfl_crawler import BaseCrawler
from crawlers.player_scraper import PlayerScraper
import unicodedata
from lxml import etree, objectify

class TeamCrawler(BaseCrawler):
    """ Provides access to the HTML table containing player data. """
    
    def getPlayersTable(self, subUrl):
        splitUrl = subUrl.split('/')
        pageId = splitUrl[len(splitUrl) - 1]

        # find the section containing the players.
        query = self.builder.buildPageDetailsFromTitleUrl(pageId, "sections")
        sectionsTree = self.__getRequest__(query)
        team = sectionsTree.xpath('/api/parse')
        teamId = team[0].get('pageid')

        lines = '[@line="Players of note" or @line="Current roster" or @line="Roster" or @line="Current roster and coaching staff"]'
        section = sectionsTree.xpath('/api/parse/sections/s' + lines)
        sectionIndex = section[0].get('index')

        # Now fetch the actual table of players.
        tableQuery = self.builder.buildSectionUrl(teamId, sectionIndex, 'text')
        playerTree = self.__getRequest__(tableQuery)

        text = etree.HTML(playerTree.xpath('/api/parse/text/text()')[0])

        # Find the table that has the teams listed. 
        return text.xpath('//table[@class="toccolours"]')[0]