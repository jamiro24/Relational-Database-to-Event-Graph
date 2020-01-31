from database.neo4j_connection import Neo4JConnection


def create_indexes(neo4j_conn: Neo4JConnection):
    neo4j_conn.query("CREATE INDEX ON :Entity(EntityType)", 'Creating index on :Entity(EntityType)')
    neo4j_conn.query("CREATE INDEX ON :Event(start)", 'Creating index on :Event(start)')
    neo4j_conn.query("CREATE INDEX ON :TempEvent(originID)", 'Creating index on :TempEvent(originID)')