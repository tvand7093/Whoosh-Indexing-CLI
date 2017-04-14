from crawlers.team_crawler import TeamCrawler
from crawlers.player_scraper import PlayerScraper

class TeamScraper(object):
	def __init__(self):
		self.player_scraper = PlayerScraper()
		self.team_crawler = TeamCrawler()

	def scrape(self, team):
		table = self.team_crawler.getPlayersTable(team['url'])
		columns = table.xpath(".//tr")[1].xpath(".//td")

		columnIdx = 0
		columnId = 0
		results = []

		for column in columns:
			columnIdx += 1
			if columnIdx % 2 == 0:
				# column separator, so skip it.
				continue
			columnId += 1
			if columnId > 3:
				# no more to proccess.
				break
			
			firstGroup = column.xpath("./b/text()")[0]
			
			playerPositions = column.xpath(".//p/b/text()")
			playerPositions.insert(0, firstGroup)

			players = column.xpath(".//ul")
			mapped = map(lambda (i, el): self.buildPlayers(team, playerPositions[i], el), enumerate(players))

			for group in mapped:
				for player in group:
					results.append(player)
		
		return results

	def buildPlayers(self, team, positionGroup, ul):
		return [self.player_scraper.scrape(team, positionGroup, player) for player in ul.xpath('./li')]
