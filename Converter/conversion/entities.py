from database.neo4j_connection import Neo4JConnection
from log.logger import Logger
from config.config import Config

log = Logger.instance()


# Creates entity # Creates event nodes
# # @neo4j: A connection to a Neo4J database
# # @config: Root configuration
def create(neo4j: Neo4JConnection, config: Config):
    entities = config['entity']
    log_name = config['log']['name']

    for entity in entities:
        label = entity['label']
        id_column = entity["id_column"]

        neo4j.query(f"""
            MATCH (n:{label})
            CALL apoc.create.node(
                ['Entity'], 
                {{
                    EntityType:'{label}', 
                    IDLog:'{log_name}' + n.{id_column}, 
                    IDraw: n.{id_column}, 
                    Log:'{log_name}', 
                    uID:'{label}{log_name}'+ n.{id_column}
                }}) yield node
            SET node+=n
        """, f"Creating entity nodes with EntityType:{label}")
