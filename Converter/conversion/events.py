from database.neo4j_connection import Neo4JConnection
from log.logger import Logger
from config.config import Config

log = Logger.instance()


# Creates event nodes
def create(neo4j: Neo4JConnection, config: Config):
    entities_config = config['entity']
    non_entities_config = config['non_entity']

    # Create events from sources that are entities
    for entity_config in entities_config:
        # Not all entity types result in events
        if 'event' in entity_config:
            event_config = entity_config['event']
            __create_temp_events(neo4j, event_config, entity_config, entities_config, True)

            for create_from in event_config['create_from']:
                __create_events(neo4j, create_from, entity_config)
            __cleanup_temp(neo4j)

    # Create events from sources that are non-entity
    for non_entity_config in non_entities_config:
        event_config = non_entity_config['event']
        __create_temp_events(neo4j, event_config, non_entity_config, entities_config, False)

        for create_from in event_config['create_from']:
            __create_events(neo4j, create_from, non_entity_config)
        __cleanup_temp(neo4j)


def __cleanup_temp(neo4j: Neo4JConnection):
    neo4j.query("""
        MATCH (e:TempEvent)
        DELETE e
        """, 'Cleaning up temp nodes')


def __form_activity(activity_config: str) -> str:
    result = ''
    lst = activity_config.split('{')
    result += f'\'{lst[0]}\''
    for item in lst[1:]:
        splt = item.split('}')
        first, second = splt[0], splt[1]
        result += f'+ent.{first}'
        if second != '':
            result += f'+{second}'
    return result


def __create_events(neo4j: Neo4JConnection, create_from: dict, entity_config: dict):
    entity_label = entity_config['label']  # label of the current entity
    start_column = create_from['start_column']
    end_column = start_column
    activity = start_column

    if 'end_column' in create_from:
        end_column = create_from['end_column']
    if 'activity' in create_from:
        activity = __form_activity(create_from['activity'])

    neo4j.query(f"""
        // Find Incident TempEvents that should generate this event
        MATCH (ent:TempEvent {{EntityType:'{entity_label}'}})
        WHERE '{start_column}' in keys(ent)
        
        // Find other matching TempEvent
        MATCH (t:TempEvent {{commonID: ent.commonID}})
        WITH ent, t
        
        CREATE (event:Event)
        SET event = t
        SET event.Activity = {activity}
        SET event.Start = ent.{start_column}
        SET event.End = ent.{end_column}
        
        WITH ent, collect(event) as events
        
        CREATE (co:Common)
        
        WITH co, events
        UNWIND events as event
        WITH co, event
        
        // Create relations between events and common nodes
        CREATE (event)-[ec:E_C {{entityType: event.entityType}}]->(co)
        
        return event, co, ec
    """, f'Creating event nodes for {entity_label}.{start_column}')


def __create_temp_events(neo4j: Neo4JConnection, event_config, entity_config: dict, entities_config: dict,
                         to_self: bool):
    entity_label = entity_config['label']  # label of the current entity
    related_entities = event_config['related_entities']  # list of entities that should relate to these events

    if to_self:
        # Create temp event nodes for the target entity type
        neo4j.query(__create_temp_events_query(entity_label, entity_config, entities_config)
                    , f'Creating temp events for {entity_label} entities')

    # Create temp event nodes for the entities related to the target entity type
    for related_entity in related_entities:
        neo4j.query(__create_temp_events_query(entity_label, entity_config, entities_config, related_entity),
                    f'Creating temp events for {related_entity} entities related to {entity_label}')


# Returns query to create temp event nodes
def __create_temp_events_query(entity_label: str, entity_config: dict, entities_config: dict,
                               related: str = None) -> str:
    match = f'MATCH (common:{entity_label})'  # matcher to find desired node with label `entity_label`
    related_config = entity_config  # config for related entity (equals current entity config if `related == None`
    related_matcher = 'common'  # matcher used for related nodes (equals 'common' if `related == None`

    if related is not None:
        related_labels = related.split(':')
        related_config = None

        for i in range(len(related_labels)):
            direction = '-->'
            related_label = related_labels[i]
            if related_label.startswith('-'):
                related_label = related_label[1:]
                direction = '<--'
            elif related_label.startswith('+'):
                related_label = related_label[1:]

            if (i + 1) == len(related_labels):
                match += f'{direction}(related:{related_label})'
                related_config = next(x for x in entities_config if x['label'] == related_label)
            else:
                match += f'{direction}(:{related_label})'

        related_matcher = 'related'

    related_id_column = related_config['id_column']  # id column of related entity type
    related_label = related_config['label']  # label of related entity type

    return f"""
            {match}
            MERGE (n:TempEvent {{originID: ID({related_matcher}), commonID: ID(common)}})
            ON CREATE SET n+={related_matcher}
            ON CREATE SET n.EntityType="{related_label}"
            ON CREATE SET n.IDraw={related_matcher}.{related_id_column}
            """
