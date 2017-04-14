
class PlayerScraper(object):
    """ Represents a way to take information from HTML and make objects from it. """

    def scrapeLink(self, li):
        path = li.xpath('./a')
        if len(path) > 0:
            return path[0].get('href')
        return ''

    def scrapeNumber(self, li):
        """ Gets the player's jersey number. """
        return li.xpath('./span/text()')[0].encode('ascii', 'ignore')

    def scrapeName(self, li):
        """ Gets the name of a player. """
        path = li.xpath('./a/text()')
        if len(path) > 0:
            return path[0]
        return ''

    def scrapeSpecialty(self, li):
        positionMapping = {
            "FB": { "name": "Fullback", "abbr": "FB" },
            "C": { "name": "Center", "abbr": "C" },
            "T": { "name": "Tackle", "abbr": "T" },
            "G": { "name": "Gaurd", "abbr": "G" },
            "DE": { "name": "Defensive End", "abbr": "DE" },
            "DT": { "name": "Defensive Tackle", "abbr": "DT" },
            "OLB": { "name": "Outside Linebacker", "abbr": "OLB" },
            "MLB": { "name": "Middle Linebacker", "abbr": "MLB" },
            "SS": { "name": "Strong Safety", "abbr": "SS" },
            "FS": { "name": "Free Safety", "abbr": "FS" },
            "S": { "name": "Safety", "abbr": "S" },
            "CB": { "name": "Corner Back", "abbr": "CB" },
            "P": { "name": "Punter", "abbr": "P" },
            "K": { "name": "Kicker", "abbr": "K" },
            "LS": { "name": "Long Snapper", "abbr": "LS" },
            "TE": { "name": "Tight End", "abbr": "TE" },
            "PR": { "name": "Punt Returner", "abbr": "PR" },
            "KR": { "name": "Kick Returner", "abbr": "KR" },
            "NT": { "name": "Nose Tackle", "abbr": "NT" },
            "ILB": { "name": "Inside Linebacker", "abbr": "ILB" },
            "LB": { "name": "Linebacker", "abbr": "LB" },
            "RS": { "name": "Return Specialist", "abbr": "RS" },
            "QB": { "name": "Quarterback", "abbr": "QB" },
            "DB": { "name": "Defensive Back", "abbr": "DB" },
        }

        playerSpecialty = li.xpath('./text()')
        if len(playerSpecialty) > 1:
            # $ sign replace is for a single edge case of bad spelling. Ideally, this would strip
            # all non alphabetic char's.
            position = playerSpecialty[1].strip().replace('$', '')

            # skip over positions that have multiple specialties as these are hard to parse.
            if "/" not in position:
                return positionMapping[position]

        return ''

    def scrapePosition(self, positionGroup):
        positionType = {
            "Quarterbacks": { "name": "Quarterback", "abbr": "QB" },
            "Running backs": { "name": "Running Back", "abbr": "RB" },
            "Wide receivers": { "name": "Wide Receiver", "abbr": "WR" },
            "Tight ends": { "name": "Tight End", "abbr": "TE" },
            "Offensive linemen":  { "name": "Offensive Lineman", "abbr": "OL" },
            "Defensive linemen":  { "name": "Defensive Lineman", "abbr": "DL" },
            "Linebackers": { "name": "Linebacker", "abbr": "LB" },
            "Defensive backs":  { "name": "Defensive Back", "abbr": "DB" },
            "Special teams":  { "name": "Special Teams", "abbr": "ST" }
        }

        return positionType[positionGroup]

    def scrape(self, team, positionGroup, listItem):
        player = {
            "name": self.scrapeName(listItem),
            "number": self.scrapeNumber(listItem),
            "url": self.scrapeLink(listItem),
            "position": self.scrapePosition(positionGroup),
            "team": team
        }

        specialty = self.scrapeSpecialty(listItem)
        if len(specialty) > 0:
            player['position']['specialty'] = specialty

        return player


