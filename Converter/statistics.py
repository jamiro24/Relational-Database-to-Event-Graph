import os

from config.config import Config
from database.neo4j_connection import Neo4JConnection
from log.logger import Logger

from statistics import counts
from statistics import degrees
from statistics import df_path_length
from statistics import basic
from statistics import diameter


config = Config()

log = Logger.instance()
# log.set_log_level(INFO)

neo4j = Neo4JConnection(config)

if not os.path.exists('statistics-csv'):
    os.makedirs('statistics-csv')

basic.calculate(neo4j, config)
counts.calculate(neo4j)
degrees.calculate(neo4j, config)
degrees.histograms_produce('degrees_histogram')

df_path_length.calculate(neo4j, config)
df_path_length.histograms_produce('df-path-length_histogram')
# diameter.calculate(neo4j)

