import os

from config.config import Config
from database.neo4j_connection import Neo4JConnection
from log.logger import Logger
from log.logger import INFO

from statistics import counts
from statistics import degrees

config = Config()

log = Logger.instance()
log.set_log_level(INFO)

neo4j = Neo4JConnection(config)

if not os.path.exists('statistics-csv'):
    os.makedirs('statistics-csv')

# counts.calculate(neo4j)
degrees.calculate(neo4j, config)
