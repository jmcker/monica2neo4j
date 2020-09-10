import neo4j

from .text import generate_queries

PROPS = [
    'id',
    'hash_id',
    'first_name',
    'last_name',
    'nickname',
    'gender',
    'gender_type',
    ('information', 'career', 'company'),
    ('information', 'career', 'job'),
    ('information', 'dates', 'birthdate', 'date'),      # TODO: 'date' is a duplicate key and gets overriden
    ('information', 'dates', 'deceased_date', 'date'),
    'is_active',
    'is_dead',
    'url'
]

PERSON_T = 'Person'
COMPANY_T = 'Company'

class Neo4jConnection():

    def __init__(self, uri, user, password):
        self.uri = uri
        self.driver = neo4j.GraphDatabase.driver(uri, auth=neo4j.basic_auth(user, password))

    def close(self):
        self.driver.close()

    def run_queries(self, queries):

        with self.driver.session() as session:

            for i, query in enumerate(queries):
                session.run(query)
                print(f'Ran query #{i}')

    def reset_database(self):

        queries = ['MATCH(n) DETACH DELETE n']
        self.run_queries(queries)

    def ingest_contacts(self, contacts):
        '''
        Clear the database and import the contacts/relationships/companies
        '''

        queries = generate_queries(contacts)
        self.run_queries(queries)
