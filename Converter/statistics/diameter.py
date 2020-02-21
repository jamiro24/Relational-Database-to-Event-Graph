from database.neo4j_connection import Neo4JConnection
from statistics import csv
from config.config import Config
import functools


def calculate(neo4j: Neo4JConnection, config: Config):
    nodetypes = ["Event", "Common", "Entity", "Log"]
    relationtypes = ["E_C", "DF", "E_EN", "L_E"]
    results = []

    for i in range(-1, len(relationtypes)):
        current_relation_types = relationtypes
        message = "calculating diameter"

        if i > 0:
            message += f"without {relationtypes[i]} relationships"
            del current_relation_types[i]

        result = neo4j.query(f"""
            match (n), (m)
            where n <> m
            AND ({functools.reduce(lambda a,b : f'n:{a} OR n:{b}', nodetypes)})
            with n, m
            match p=shortestPath((n)-[:{functools.reduce(lambda a,b : f'{a}|{b}', current_relation_types)}*]-(m))
            return ID(n), ID(m), length(p)
            order by length(p) desc limit 1
        """, message)

        if i > 0:
            results.append([relationtypes[i]] + result[0])
        else:
            results.append(['-'] + result[0])

    csv.write(results, ["without", "source", "target", "length"], "diameter")


def calculate_v2(neo4j: Neo4JConnection, config: Config):
    nodetypes = ["Event", "Common", "Entity", "Log"]

    adj_matrix = neo4j.query(f"""
        match (n), (m)
        WHERE ({functools.reduce(lambda a,b : f'n:{a} OR n:{b}', nodetypes)})
        return ID(n), ID(m),
        case 
        when (n)-->(m) then 1
        else 0
        end as value
    """, "calculating the adjacency matrix")

    csv.write(adj_matrix, ["source", "target", "connects"], "adjacency matrix")
