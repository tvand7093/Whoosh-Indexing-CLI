
from yelp.client import Client
from yelp.oauth1_authenticator import Oauth1Authenticator
from state_seeder import StateSeeder
from pymongo import MongoClient, TEXT
from config import Config
import urllib

def mongoConnect(params):
    password = urllib.quote_plus(params.MONGO_PASS)

    uri = "mongodb://{0}:{1}@{2}/{3}".format(params.MONGO_USER, 
        password,
        params.MONGO_HOST,
        params.MONGO_DB)

    return MongoClient(host=uri)[params.MONGO_DB]

def insertRestaurantsForCity(db, restaurants):
    insertedIds = db.restaurants.insert_many(restaurants)
    db.restaurants.create_index([
		('Name', TEXT),
		('City', TEXT),
		('URL', TEXT),
		('Rating', TEXT),
		('State', TEXT),], default_language='english')

def buildRestaurant(city, state, business):
    result = {
        "Name" : business.name,
        "City" : city,
        "URL" : business.url,
        "Rating" : business.rating
    }

    if state != None:
        result["State"] = state
    return result

auth = Oauth1Authenticator(
    consumer_key="REiAz8Bdo4ZDdqoSeZ_CHw",
    consumer_secret="TTbM3viyQyvT4ED4uEpPZEIgbXY",
    token="gdFMM-VX3R6nFblRMTFJj2cXELQxVFAI",
    token_secret="qaTy_1Y1PRVMfjLS4HaDy2HWuwk"
)

client = Client(auth)


params = {
    'term': 'food',
    'limit' : 20,
}

with open("data_imports/yelp_scraper/city_names.txt") as f:
    lines = f.readlines()

states = StateSeeder()

submissionList = []

for city in lines:
    print "Searching for " + city
    locationParam = city.strip() + ", USA"
    results = client.search(locationParam, **params)
    # print "Found ", len(results.businesses) , " businesses!"
    # print results.businesses[0].name
    # print results.businesses[0].url
    state = states.lookupState(results.businesses[0].location.state_code)
    mapped = map(lambda (item): buildRestaurant(city.strip(), state, item), results.businesses)
    submissionList.append(mapped)

print "CONNECTING"
# Connect to database then insert every item in submissionList
db = mongoConnect(Config())
db.restaurants.drop()
print "INSERTING"
for item in submissionList:
    insertRestaurantsForCity(db, item)
print "DONE"