import json

PROPS = [
    'id',
    'hash_id',
    'name',
    'first_name',
    'last_name',
    'nickname',
    'complete_name',
    'initials',
    'gender',
    'gender_type',
    'description',
    ('information', 'career', 'company'),
    ('information', 'career', 'job'),
    ('information', 'dates', 'birthdate', 'date'),      # TODO: 'date' is a duplicate key and gets overriden
    ('information', 'dates', 'deceased_date', 'date'),
    'is_active',
    'is_dead',
    'company',
    'url'
]

# Node types
COMPANY_T = 'Company'

# Relationship types
WORK_REL_T = 'work'
ORG_REL_T = 'organization'
TAG_REL_T = 'tag'

def generate_contacts(contacts):
    '''
    Generate queries for a list of contacts, their companies,
    and their relationships.
    '''

    queries = set()

    for contact_api_obj in contacts:
        contact_queries = generate_contact(contact_api_obj)
        queries.update(contact_queries)

    queries = sorted(queries, key=_create_queries_first)

    return queries

def generate_contact(contact_api_obj):
    '''
    Generate queries for a single contact, its companies,
    and its relationships.
    '''

    queries = set()

    contact_query = generate_node(contact_api_obj)

    # Handle companies
    career_api_obj = contact_api_obj['information']['career']
    company_queries = generate_company_relationships(contact_api_obj, career_api_obj)

    # Normal Monica relationships
    relationship_queries = generate_relationships(contact_api_obj, contact_api_obj['information']['relationships'])

    # Tags
    tag_queries = generate_tag_relationships(contact_api_obj, contact_api_obj['tags'])

    queries.add(contact_query)
    queries.update(company_queries)
    queries.update(relationship_queries)
    queries.update(tag_queries)

    return queries

def generate_relationships(api_obj, relationship_groups):
    '''
    Create all relationships in the list of relationship groups that
    belong to `api_obj`.

    Relationships in the groups are in form `rel_group_contact` is a
    `relationship` of `api_obj`.
    '''

    # This is typically a contact
    of_contact = api_obj

    relationships = set()

    for rel_group_type, rel_group in relationship_groups.items():

        for relationship_wrapper in rel_group['contacts']:
            contact_is = relationship_wrapper['contact']
            relationship = relationship_wrapper['relationship']

            query = generate_relationship(contact_is, relationship, of_contact, rel_group_type=rel_group_type)
            relationships.add(query)

    return relationships

def generate_relationship(api_obj_is, relationship, of_api_obj, rel_group_type=None):
    '''
    Create a single relationship
    '''

    node_label_is = api_obj_is['object'].capitalize()
    node_id_is = api_obj_is['id']

    of_node_label = of_api_obj['object'].capitalize()
    of_node_id = of_api_obj['id']

    relationship_id = relationship['id']
    relationship_name = relationship['name']

    if (relationship_name is None):
        relationship_name = ''

    relationship_name = relationship_name.upper()
    relationship_name = relationship_name.replace(' ', '_')
    relationship_name = relationship_name.replace('-', '_')
    relationship_type = json.dumps(rel_group_type)

    query_parts = [
        f'MATCH (a:{node_label_is}), (b:{of_node_label})',
        f'WHERE a.id = {node_id_is} AND b.id = {of_node_id}',
        f'CREATE (a)-[:{relationship_name} {{ id: {relationship_id}, type: {relationship_type} }}]->(b)',
        f'RETURN a, b'
    ]

    return '\n'.join(query_parts)

def generate_tag_relationships(api_obj, tag_api_objects):
    '''
    Handle creating and adding relationhips between a tag
    and another API object (usually a contact).
    '''

    queries = set()

    for tag_api_object in tag_api_objects:
        tag_queries = generate_tag_relationship(api_obj, tag_api_object)

        queries.update(tag_queries)

    return queries

def generate_tag_relationship(api_obj, tag_api_object):
    '''
    Handle creating and adding the relationhips between a tag
    and another API object (usually a contact).
    '''

    queries = set()

    tag_query = generate_node(tag_api_object)

    # Tag -> API Object
    tag_rel = {
        'id': hash(TAG_REL_T),
        'name': 'INCLUDES'
    }

    tag_rel_query = generate_relationship(
        tag_api_object,
        tag_rel,
        api_obj,
        rel_group_type=TAG_REL_T
    )

    # API Object -> Tag
    obj_rel = {
        'id': hash(TAG_REL_T),
        'name': 'PART_OF'
    }

    obj_rel_query = generate_relationship(
        api_obj,
        obj_rel,
        tag_api_object,
        rel_group_type=TAG_REL_T
    )

    queries.add(tag_query)
    queries.add(tag_rel_query)
    queries.add(obj_rel_query)

    return queries

def generate_company_relationships(api_obj, career_api_obj):
    '''
    Handle creating and adding relationships between a company
    and another API object (usually a contact).

    This requires some special handling since comapnies aren't
    actually objects in Monica.
    '''

    queries = set()

    if (api_obj is None or career_api_obj is None):
        return queries

    company_name = career_api_obj['company']
    job_title = career_api_obj['job']

    if (company_name is None and job_title is None):
        return queries

    # Companies aren't officially objects in Monica
    # Fake it ourselves
    career_api_obj['id'] = hash(company_name)
    career_api_obj['object'] = COMPANY_T
    career_api_obj['name'] = company_name

    company_query = generate_node(career_api_obj)

    # Employee -> Company
    job_rel_wrapper = {
        'id': hash(company_name),
        'name': 'PART_OF' if job_title is None else job_title
    }

    job_rel_query = generate_relationship(
        api_obj,
        job_rel_wrapper,
        career_api_obj,
        rel_group_type=ORG_REL_T
    )

    # Company -> Employee
    company_rel_wrapper = {
        'id': hash(ORG_REL_T),
        'name': 'INCLUDES'
    }

    company_rel_query = generate_relationship(
        career_api_obj,
        company_rel_wrapper,
        api_obj,
        rel_group_type=ORG_REL_T
    )

    queries.add(company_query)
    queries.add(job_rel_query)
    queries.add(company_rel_query)

    return queries

def generate_node(api_obj):

    node_label = api_obj['object'].capitalize()
    props = extract_props(api_obj)
    props_str = props_to_str(props)

    query = f'CREATE (n:{node_label} {props_str}) RETURN n'

    return query

def safe_walk(api_obj, keys):

    curr = api_obj
    for key in keys:
        if (curr is None):
            break

        curr = curr.get(key, None)

    return curr

def extract_props(api_obj):

    result = {}
    for prop_name in PROPS:

        # Use json.dumps to make sure everything is quoted and escaped properly
        if (type(prop_name) == str):
            if (prop_name in api_obj):
                result[prop_name] = json.dumps(api_obj.get(prop_name))

        elif (type(prop_name) in {tuple, list}):
            value = safe_walk(api_obj, prop_name)
            if (value is not None):
                result[prop_name[-1]] = json.dumps(value)

        else:
            raise Exception(f'Invalid prop type: {type(prop_name)}')

    return result

def props_to_str(props):

    prop_strs = []
    for key, value in props.items():
        prop_strs.append(f'{key}: {value}')

    return f'''{{ {', '.join(prop_strs)} }}'''

def _create_queries_first(query: str):
    if (query.startswith('CREATE')):
        return 1
    return 100
