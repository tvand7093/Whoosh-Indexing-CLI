
from settings import Settings
from indexes import SchemaBuilder

def test(db):
	schemaBuilder = SchemaBuilder()
	doc = db.players.find_one()
	built = schemaBuilder.build_values(doc)
	print built

def main():
	db = Settings().db
	test(db)
	return 0

if __name__ == '__main__': 
	main()
