# monica2neo4j #

Create a Neo4j graph database using details and relationships from [Monica](https://github.com/monicahq/monica)

### Setup ###

```bash
# Dependencies
virtualenv env
source ./env/bin/activate
pip install -r requirements.txt

# TODO: setup secrets file/auth
# Currently looks for secrets.json in the current directory
```

### Usage ###

```console
$ python -m monica2neo4j --help
usage: monica2neo4j [-h] [--monica MONICA_BASE] [--neo4j NEO4J_URL] [--print]
                    [--wipe] [--force]

Copy contact details and relationships from Monica to a Neo4j graph database

optional arguments:
  -h, --help            show this help message and exit
  --monica MONICA_BASE, -m MONICA_BASE
                        HTTP(s) address of the desired Monica instance
  --neo4j NEO4J_URL, -n NEO4J_URL
                        Bolt address for the desired Neo4j instance
  --print, -p           Print the Neo4j queries instead of running them
  --wipe, -w            Clear the ENTIRE database before populating it from
                        Monica. ALL nodes and relationships will be removed
  --force, -f           Do not prompt for confirmation of prune or wipe



$ python -m monica2neo4j --print --monica https://app.monicahq.com
...
```
