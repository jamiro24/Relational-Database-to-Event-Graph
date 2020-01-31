from database.neo4j_connection import Neo4JConnection
from log.logger import Logger
from config.config import Config

log = Logger.instance()


# Creates entity nodes
def create(neo4j: Neo4JConnection, config: Config):
    entities = config['entity']
    log_name = config['log']['name']

    for entity in entities:
        label = entity['label']
        id_column = entity["id_column"]

        neo4j.query(f"""
            MATCH (n:{label})
            WITH DISTINCT n.{id_column} as id
            CALL apoc.create.node(
                ['Entity'], 
                {{
                    EntityType:'{label}', 
                    ID:'{log_name}'+id, 
                    IDraw:id, Log:'{log_name}', 
                    uID:'{label}{log_name}'+id
                }}) yield node
            RETURN node
        """, f"Creating entity nodes with EntityType:{label}")
