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

After running this (or any) command sucessfully, a file will be placed in the local directory named `stats.json`. This file
is just used as a temporary file that contains the overall size of the index (field length). This is required because the index
fields are generated on the fly given the dynamic nature of a document based database such as MongoDB. When pulling data from the database,
the index fields are populated dynaimcally using just the indexed column. For this reason, the data contained in each index field may not
necessarily match up to that of another record. 

### Searching the index

To search the index, do the following command. The command will return the to 10 results (full document) for the search parameter, and it will also display the score acheived by the query. The runtime of the query is also displayed above the query results.

```
python main.py --search wa index-name
```

This will query an index in the `index-name` directory for anything with the term 'wa' in it.