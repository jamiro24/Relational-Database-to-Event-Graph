from database.neo4j_connection import Neo4JConnection
from log.logger import Logger

log = Logger.instance()


def event_graph(neo4j: Neo4JConnection):
    warning()

    for node_type in ['Entity', 'Event', 'Log', 'Common', 'TempEvent']:
        neo4j.query(f"""
                MATCH (n:{node_type})
                OPTIONAL MATCH (n)-[r]-()
                DELETE n,r
            """, f'Cleaning up `{node_type}` nodes and their relationships')


def warning():
    answer = ""
    while answer not in ["y", "n"]:
        answer = input(f"This will delete any existing event graph . Is this okay [Y/N]? ").lower()
    if answer != "y":
        log.info("Did not clear event graph")
        exit(1)
