from database.neo4j_connection import Neo4JConnection
from statistics import csv


def calculate(neo4j: Neo4JConnection, config: dict):

    nodetypes = ["Event", "Common", "Entity", "Log"]
    results = []

    for nodetype in nodetypes:
        for dir in ["<", ">"]:
            result = neo4j.query(f"""
                MATCH (u:{nodetype})
                RETURN avg(apoc.node.degree(u,'{dir}')) as average,
                stdev(apoc.node.degree(u,'{dir}')) as stdev,
                max(apoc.node.degree(u,'{dir}')) as max,
                min(apoc.node.degree(u,'{dir}')) as min
            """)

            namemod = "in" if dir == "<" else "out"
            results = results.append([f'{nodetype}-{namemod}'] + result[0])

    csv.write(results, ['average', 'stdev', 'max', 'min'], "degrees")
