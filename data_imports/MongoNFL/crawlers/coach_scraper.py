
from coach_crawler import CoachCrawler
from dateutil.parser import parse
from datetime import date
from seeders import StateSeeder

class CoachScrapeResult(object):
    """ Represnts the results of a scraping. """

    def __init__(self, name, dob, city, state, image):
        """ Creates a new instance. """

        """ The name of the coach. """
        self.name = name
        """ The date of birth of the coach. """
        self.dateOfBirth = dob

        """ The city the coach was born in. """
        self.birthCity = city
        """ The state the coach was born in. """
        self.birthState = state

        """ The web url image for this coach. """
        self.image = image


class CoachScraper(object):
    """ Represents a way to take information from HTML and make objects from it. """

    """ The crawler used to find the webpages needed for scraping. """
    crawler = CoachCrawler()

    def scrapeDOB(self, table):
        """ Obtains the date of birth value from a table element. """
        dobNode = table.xpath('.//span[@class="bday"]/text()')[0]
        return parse(dobNode)

    def scrapeHometown(self, table):
        """ Obtains the hometown value from a table element. """
        seeder = StateSeeder()

        # Get the starting point for birth city
        cityNodes = table.xpath('.//span[@class="nowrap"][text() = "Place of birth:"]')
        if len(cityNodes) == 0:
            return (None, None)
        
        # Now traverse parent nodes to find the city/state info.
        cityNodes = cityNodes[0].getparent().getparent().xpath('./td/a/text()')

        if len(cityNodes) == 0:
            return (None, None)

        # Format the city
        city = cityNodes[0]
        split = city.split(', ')

        # lookup the state abbreviation
        state = seeder.lookupState(split[1])

        # Return the values for the new city.
        return (split[0], state)

    def scrapeName(self, table):
        """ Gets the name of a coach. """
        return table.xpath('./caption/text()')[0]

    def scrapeImage(self, table):
        """ Gets the image for the coach. """
        imageNodes = table.xpath('.//img')
        if len(imageNodes) > 0:
            return imageNodes[0].get('src')
        else:
            return None

    def scrapeAll(self, coachUrl):
        """ Scrapes all relevant information for a coach and returns a new coach result. """

        if coachUrl == None:
            # Use unknown coach.
            return None

        try:
            # Fetch the page HTML table content.
            table = self.crawler.getDetailsTable(coachUrl)

            # Get the coaches properties
            name = self.scrapeName(table)
            dob = self.scrapeDOB(table)
            city, state = self.scrapeHometown(table)
            image = self.scrapeImage(table)

            # Return findings
            return CoachScrapeResult(name, dob, city, state, image)
        except IndexError as err: 
            print "Handled error:", err
            return None


