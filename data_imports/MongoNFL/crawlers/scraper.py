
from nfl_crawler import BaseCrawler
from coach_scraper import CoachScraper, CoachScrapeResult
from seeders import StateSeeder
from datetime import date

class Scraper(BaseCrawler):
    """ Scrapes and inserts data from the NFL page. """

    coachScraper = CoachScraper()

    def insertConference(self, conference):
        """ Inserts a new conference and returns its abbreviation. """
        abbr = ''
        if conference[0] == 'N': 
            abbr = 'NFC'
        else:
            abbr = 'AFC'

        return {
            "name": conference,
            "abbr": abbr
        }

    def insertCity(self, city, state):
        """ Insert a new city into the database and return the new ORM object. """
        if city == None and state == None:
            return None

        return {
            "city": city,
            "state": state
        }

    def insertStadium(self, city, stadiumName, capacity, coordinates):
        """ Insert a new stadium into the database and return the new ORM object. """
        return {
            "name": stadiumName,
            "capacity": capacity,
            "coordinates": coordinates,
            "city": city
        }

    def insertDivision(self, division, conference):
        """ Insert a new division into the database and return the new ORM object. """
        return {
            "name": division,
            "conference": conference
        }
   
    def insertCoach(self, name, dob, city, image):
        """ Insert a new coach into the database and return the new ORM object. """
        coach = {
            "name": name,
            "dob": dob,
            "image_url": image
        }

        if city != None:
            coach["born_in"] = city
        
        return coach


    def insertTeam(self, name, url, coach, city, division, stadium):
        """ Insert a new team into the database and return the new ORM object. """

        team = {
            "name": name,
            "home_city": city,
            "division": division,
            "stadium": stadium,
            "url": url
        }

        if coach != None:
            team["head_coach"] = coach

        return team

    def parseNode(self, node):
        """ Parses a given HTML node and obtains context information for teams and conferences. """
        
        # Obtain long; lat coordinates for stadium
        geo = node.xpath('.//span[@class="geo"]/text()')
        coordinates = ''
        if len(geo) > 0:
            coordinates = geo[0]

        # Obtain the name of the current team. If none, it is a weird row so skip it.
        teamText = node.xpath('./td/b/a/text()')
        teamLink = node.xpath('./td/b/a')
        team = ''
        if len(teamText) > 0:
            team = teamText[0]
        else: 
            return None

        teamUrl = ''
        if len(teamLink) > 0:
            teamUrl = teamLink[0].get('href')
        
        
        # Metadata will contain stadium name and city/state information.
        metadata = node.xpath('./td/a/text()')

        # Coach URL
        links = node.xpath('./td/a')
        coachLink = None
        if len(links) != 0:
            coachLink = links[len(links)-1].get('href')

        # Others will contain the stadium capacity.
        others = node.xpath('./td/text()')

        # Get the division
        divisionText = node.xpath('./th/a/text()')

        division = ''
        if(len(divisionText) > 0):
            division = divisionText[0] 

        # Another bad row, so skip it.
        if len(metadata) < 2:
            return { metadata: None }

        # Parse out the city information. Original format is: city, state
        cityString = metadata[0].replace(u'\u2013', '-')
        cityParts = cityString.split(', ')
        city = cityParts[0]
        state = cityParts[1]

        # Get the stadium name
        stadium = metadata[1].replace(u'\u2013', '-')

        # make sure we parse out the comma in the number like: 27,000
        capacity = others[0].replace(',', '')

        # Return a dictionary of the context values.
        return {
            'city': city,
            'state': state,
            'coachLink': coachLink,
            'stadium': stadium,
            'capacity': capacity,
            'division': division,
            'team': team,
            'teamLink': teamUrl,
            'coordinates': coordinates
        }



    def scrape(self, htmlNode):
        """ Scrapes the main NFL page for base information of teams, stadiums, coaches, etc... """

        # the conference is weird, and so we have to keep track of when it changes,
        # rather than just grab it right away since it is contextual to the team.
        currentConference = ''
        currentDivision = ''
        teams = []

        for node in htmlNode:
            # Conferences are laid out wierd, so they are an edge case.
            conferenceText = node.xpath('./th/a/span/text()')
            if len(conferenceText) > 0:
                currentConference = self.insertConference(conferenceText[0])
                
            # Parse the rest of the HTML like normal.
            # Context will be a dictionary of values for the given team 'context'
            context = self.parseNode(node)

            # Invalid format, so skip this table row.
            if context == None:
                continue

            if context['division'] != '':
                currentDivision = context['division']

            states = StateSeeder()
            cityState = states.lookupState(context['state'])

            # Insert all the database records.
            city = self.insertCity(context['city'], cityState)
            stadium = self.insertStadium(city, context['stadium'], context["capacity"], context['coordinates'])
            division = self.insertDivision(currentDivision, currentConference)

            # Get the coaches date of birth
            coachInfo = self.coachScraper.scrapeAll(context['coachLink'])

            # Only add a coach if one was actually found/properly constructed
            coach = None
            if coachInfo != None:
                coachCity = self.insertCity(coachInfo.birthCity, coachInfo.birthState)
                coach = self.insertCoach(coachInfo.name, coachInfo.dateOfBirth, coachCity, coachInfo.image)

            # Always add a team.
            team = self.insertTeam(context['team'], context['teamLink'], coach, city, division, stadium)
            teams.append(team)

        return teams