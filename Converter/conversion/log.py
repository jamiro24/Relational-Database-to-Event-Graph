from database.neo4j_connection import Neo4JConnection


def create(neo4j: Neo4JConnection):
    neo4j.query("""
        CREATE (l:Log {ID: 'BPI14'})
        WITH l
        Match (e:Event)
        CREATE (l)-[r:L_E]->(e)
        RETURN *
    """, 'Creating Log node with L_E relations')
