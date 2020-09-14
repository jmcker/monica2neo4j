# monica2neo4j #

Create a Neo4j graph database using details and relationships from [Monica](https://github.com/monicahq/monica)

## Setup ##

```bash
# Dependencies
virtualenv env
source ./env/bin/activate
pip install -r requirements.txt

# TODO: setup secrets file/auth
# Currently looks for secrets.json in the current directory
```

## Usage ##

```console
$ python -m monica2neo4j --help
usage: monica2neo4j [-h] [--monica MONICA_BASE_URL] [--neo4j NEO4J_URL]
                    [--print] [--wipe] [--force]

Copy contact details and relationships from Monica to a Neo4j graph database

optional arguments:
  -h, --help            show this help message and exit
  --monica MONICA_BASE_URL, -m MONICA_BASE_URL
                        HTTP(S) address of the desired Monica instance
  --neo4j NEO4J_URL, -n NEO4J_URL
                        Bolt address for the desired Neo4j instance
  --print, -p           Print the Neo4j queries instead of running them
  --wipe, -w            Clear the ENTIRE database before populating it from
                        Monica. ALL nodes and relationships will be removed
  --force, -f           Do not prompt for confirmation of prune or wipe



$ python -m monica2neo4j --print --monica https://app.monicahq.com
...
```

## Example Queries ##

Once the data is ingested, here are some interesting queries to try out.

Note: If Neo4j isn't displaying a helpful field as the node name, you can switch it:
1. After running a query, select the colored node label (i.e. `Contacts`) at the top of the result
1. Change the `Caption` setting to a different property

```js
// Everything
MATCH (n) RETURN n
```

```js
// Contacts
MATCH (n:Contact) RETURN n
```

```js
// Companies
MATCH (n:Company) RETURN n
```

```js
// Tags
MATCH (n:Tag) RETURN n
```

```js
// Gender Search
// You can add other properties to the {} list. This will return
// only nodes that have all of the matching properties
MATCH (n:Contact {gender: 'Woman'}) RETURN n
```

```js
// Contacts at a Company
WITH
  'Hotel Winden' AS company
MATCH p=(a:Contact)-[r]-(b:Company)
WHERE b.name = company
RETURN p
```

```js
// Contacts in a Tag
WITH
  '1986' AS tag
MATCH p=(a:Contact)-[r]-(b:Tag)
WHERE b.name = tag
RETURN p
```

```js
// Shortest Path
// Find the shortest way that two people know each other
WITH
  'Hannah' AS first_name_a,
  'Helge' AS first_name_b
MATCH p=shortestPath((a:Contact)-[r*..5]-(b:Contact))
WHERE
  a.first_name = first_name_a
  AND b.first_name = first_name_b
RETURN p
```



**The following queries work/look much better if auto-join is turned off.**
1. In the Neo4j browser, click the settings icon in the bottom left
1. Uncheck `'Connect result nodes'`



```js
// Companies & Employees
MATCH p=(a:Company)-[r1]-(b:Contact)
RETURN p
```

```js
// Family Tree
// A family tree like graph with some generation-skipping or 'redundant'
// relationships excluded so that it flows correctly
MATCH p=(a:Contact)-[r]-(b:Contact)
WHERE (
    r.name IN ['spouse']
) OR (
  r.type IN ['family']
  AND NOT r.name IN ['grandparent', 'grandchild', 'sibling']
)
RETURN p
```

```js
// Family by last name plus spouses
WITH
  'Doppler' AS last_name
MATCH p=((a:Contact)-[r]-(b:Contact))
WHERE
  a.last_name = last_name
  AND (
    b.last_name = last_name
    OR r.name IN ['spouse']
  )
RETURN p
```

```js
// Social Circle
// Find all the direct and indirect relationships between two people
// You can increase how many 'hops' this will include by changing the number in 'r*..3'
// You can require that the path contain only certain types/names of relationships in all(...)
// You can exclude certain relationship types/names from the path in none(...)
WITH
  'Jonas' AS first_name_a,
  'Bartosz' AS first_name_b
MATCH p=((a:Contact)-[r*..3]-(b:Contact))
WHERE
  a.first_name = first_name_a
  AND b.first_name = first_name_b
  AND all(
    rel in r WHERE
      rel.type IN ['friend']
      AND rel.name IN ['friend']
  )
  AND none(
    rel in r WHERE
      rel.type IN []
      AND rel.name IN []
  )
RETURN p
```
