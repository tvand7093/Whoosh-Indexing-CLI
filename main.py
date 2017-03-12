
from settings import Settings

def main():
	db = Settings().db
	print db.collection_names()
	
	return 0

if __name__ == '__main__': 
	main()
