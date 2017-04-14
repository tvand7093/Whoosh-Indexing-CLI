
from crawlers.nfl_crawler import NFLCrawler
from crawlers.scraper import Scraper
from crawlers.coach_scraper import CoachScraper
from crawlers.team_scraper import TeamScraper

from pymongo import MongoClient, TEXT
from config import Config

import urllib
import os

def mongoConnect(params):
    password = urllib.quote_plus(params.MONGO_PASS)

    uri = "mongodb://{0}:{1}@{2}/{3}".format(params.MONGO_USER, 
        password,
        params.MONGO_HOST,
        params.MONGO_DB)

    return MongoClient(host=uri)[params.MONGO_DB]

def reset(db):
    """ Resets the database by deleting every record in every table. """
    
    print "Resetting database state..."
    db.teams.drop()
    db.players.drop()
    print "Database reset"

def insertPlayers(db, players):
    insertedIds = db.players.insert_many(players)
    db.players.create_index([
        ('name', TEXT),
        ('url', TEXT),
        ('number', TEXT),
        ('team.name', TEXT),
        ('position.name', TEXT)], default_language='english')
    return insertedIds.inserted_ids

def insertTeams(db, teams):
    db.teams.insert_many(teams)
def scrape(db):
    """ Main method for scraping all relevant data. """

    print "Scraping data..."
    # Build scrapers
    nfl = NFLCrawler()
    teamScraper = TeamScraper()
    team = Scraper()

    # Scrape data
    html = nfl.getClubsHtml()
    teams = team.scrape(html)

    # add the list of players to a team.
    for team in teams:
        players = teamScraper.scrape(team)
        playerIds = insertPlayers(db, players)
        team['players'] = playerIds

    insertTeams(db, teams)
    print "Done scraping data..."

def main():
    # Get environment variables
    config = Config()
    if not config.wasLoaded:
        return

    # Got variables, continue to process.
    db = mongoConnect(config)
    reset(db)
    scrape(db)

if __name__ == "__main__":
    main()