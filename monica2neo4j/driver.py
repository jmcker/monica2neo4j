import sys

import neo4j

from .generate import generate_contacts

class Neo4jConnection():

    def __init__(self, uri, user, password):
        self.uri = uri
        self.driver = neo4j.GraphDatabase.driver(uri, auth=neo4j.basic_auth(user, password))

    def close(self):
        self.driver.close()

    def run_queries(self, queries):

        with self.driver.session() as session:

            for i, query in enumerate(queries):
                try:
                    session.run(query)
                except Exception as e:
                    print('')
                    print('Query failed:')
                    print(str(e))
                    print('')
                    print('Query:')
                    print(query)
                    sys.exit(1)

                print(f'Completed query #{i}')

    def reset(self, force=False):
        '''
        Remove all nodes and relationships form the database
        '''

        if (not force):
            confirm = str(input('Are you sure you want to remove all nodes and relationships? [y/N] '))

            if (confirm.lower() not in {'y', 'yes'}):
                print('Aborted')
                sys.exit(1)

        queries = ['MATCH(n) DETACH DELETE n']
        self.run_queries(queries)

    def ingest_contacts(self, contacts):
        '''
        Import contacts/relationships/companies
        '''

        queries = generate_contacts(contacts)
        self.run_queries(queries)
