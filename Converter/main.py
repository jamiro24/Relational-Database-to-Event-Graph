from config.config import Config
from database.neo4j_connection import Neo4JConnection
from log.logger import Logger
from log.logger import INFO
from conversion import cleanup
from conversion import indexes
from conversion import entities
from conversion import events
from conversion import e_en
from conversion import df
from conversion import log as lognode


config = Config()

log = Logger.instance()
log.set_log_level(INFO)

neo4j = Neo4JConnection(config)

cleanup.event_graph(neo4j)
indexes.create_indexes(neo4j)
entities.create(neo4j, config)
events.create(neo4j, config)
e_en.create(neo4j)
df.create(neo4j)
lognode.create(neo4j)
