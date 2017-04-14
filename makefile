

players:
	python ./data_imports/MongoNFL/main.py

food:
	python ./data_imports/yelp_scraper/main.py

rebuild: players food
