from config.config import Config
from database.neo4j_connection import Neo4JConnection
from log.logger import Logger
from log.logger import INFO

config = Config()

log = Logger.instance()
log.set_log_level(INFO)

neo4j_config = config['connection']['neo4j']
neo4j_connection = Neo4JConnection(
    jdbc=neo4j_config['jdbc'],
    user=neo4j_config['user'],
    pw=neo4j_config['password']
)

result = neo4j_connection.query("""
match (e:Event) return count(e)
""", 'Counting event nodes')
log.info(result)
