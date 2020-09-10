import json

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

def generate_queries(contacts):

    contact_nodes = set()
    company_nodes = set()
    relationships = set()

    for contact in contacts:
        props = extract_contact_props(contact)

        # Create contact
        contact_id = props['id']

        prop_str = props_to_str(props)
        contact_node = f'(:{PERSON_T} {prop_str})'
        contact_nodes.add(contact_node)

        # Create company
        company_name = props['company']

        prop_str = props_to_str({ 'name': company_name })
        company_node = f'(:{COMPANY_T} {prop_str})'
        company_nodes.add(company_node)

        # Create relationship
        for rel_group_type, rel_group in contact['information']['relationships'].items():

            rel_group_type = json.dumps(rel_group_type)

            for relationship in rel_group['contacts']:
                opposite_id = relationship['contact']['id']
                relationship_id = relationship['relationship']['id']

                relationship_name = relationship['relationship']['name']
                relationship_name = relationship_name.upper()
                relationship_name = relationship_name.replace(' ', '_')
                relationship_name = relationship_name.replace('-', '_')

                # print(f'{opposite_id} - {relationship_name} -> {contact_id}')
                query = f'''
                    MATCH (a:{PERSON_T}), (b:{PERSON_T})
                    WHERE a.id = {opposite_id} AND b.id = {contact_id}
                    CREATE (a)-[:{relationship_name} {{ id: {relationship_id}, type: {rel_group_type} }}]->(b)
                    RETURN a, b
                '''
                relationships.add(query)

        # Create contact -> company relationship
        query = f'''
            MATCH (a:{PERSON_T}), (b:{COMPANY_T})
            WHERE a.id = {contact_id} AND b.name = {company_name}
            CREATE (a)-[:PART_OF]->(b)
            CREATE (b)-[:INCLUDES]->(a)
            RETURN a, b
        '''
        relationships.add(query)

    contact_query = f'''CREATE {', '.join(contact_nodes)}'''
    company_query = f'''CREATE {', '.join(company_nodes)}'''

    all_queries = []

    if (len(contact_nodes) > 0):
        all_queries.append(contact_query)
    if (len(company_nodes) > 0):
        all_queries.append(company_query)

    all_queries.extend(relationships)

    return all_queries

def safe_walk(contact, keys):

    curr = contact
    for key in keys:
        if (curr is None):
            break

        curr = curr.get(key, None)

    return curr

def extract_contact_props(contact):

    result = {}
    for prop_name in PROPS:

        # Use json.dumps to make sure everything is quoted and escaped properly
        if (type(prop_name) == str):
            result[prop_name] = json.dumps(contact.get(prop_name, None))

        elif (type(prop_name) == tuple):
            result[prop_name[-1]] = json.dumps(safe_walk(contact, prop_name))

        else:
            raise Exception(f'Invalid prop type: {type(prop_name)}')

    return result

def props_to_str(props):

    prop_strs = []
    for key, value in props.items():
        prop_strs.append(f'{key}: {value}')

    return f'''{{ {', '.join(prop_strs)} }}'''
