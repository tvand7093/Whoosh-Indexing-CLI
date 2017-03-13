# Whoosh-Indexing-CLI
A project for building and searching a Whoosh! based index.

## Pip Dependencies

- [python-dotenv](https://github.com/theskumar/python-dotenv) `pip install python-dotenv`
- [PyMongo](https://api.mongodb.com/python/current/) `pip install pymongo`
- [Whoosh!]() `pip install Whoosh`

## Running the code

The program is built as a command line interface that allows you to rebuild and search the index.
To do this, do the following:

### Building an index
The following command will pull from the database and build a local index in a folder named `index-name`. This **WILL** delete
any pre-existing index.

```
python main.py --build index-name
```

### Searching the index

To search the index, do the following command. The command will return the to 10 results (full document) for the search parameter, and it will also display the score acheived by the query. The runtime of the query is also displayed above the query results.

```
python main.py --search wa index-name
```

This will query an index in the `index-name` directory for anything with the term 'wa' in it.