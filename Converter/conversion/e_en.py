from database.neo4j_connection import Neo4JConnection


# Creates een relationships
# @neo4j: A connection to a Neo4J database
def create(neo4j: Neo4JConnection):
    neo4j.query("""
        MATCH (ev:Event)
        MATCH (en:Entity {IDraw: ev.IDraw, EntityType:ev.EntityType})
        CREATE (ev)-[r:E_EN]->(en)
        SET r.EntityType = en.EntityType
    """, 'Creating E_EN relations')
