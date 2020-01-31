from database.neo4j_connection import Neo4JConnection


def create(neo4j: Neo4JConnection):
    neo4j.query("""
        MATCH (n:Entity)
        MATCH (n)-[]-(ev)
        
        WITH n, ev as nodes ORDER BY ev.Start, ID(ev)
        WITH n, collect(nodes) as nodeList
        WITH n, apoc.coll.pairsMin(nodeList) as pairs
        UNWIND pairs as pair
        WITH n, pair[0] as first, pair[1] as second
        
        CREATE (first)-[df:DF]->(second)
        SET df.EntityType = n.EntityType
        SET df.EntityId = n.ID
        RETURN null
    """, 'Creating DF relations')
