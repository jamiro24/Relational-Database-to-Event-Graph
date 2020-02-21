from database.neo4j_connection import Neo4JConnection
from statistics import csv
from config.config import Config
import functools


def calculate(neo4j: Neo4JConnection, config: Config):

    nodetypes = ["Event", "Common", "Entity", "Log"]
    relationtypes = ["E_C", "DF", "E_EN", "L_E"]
    results = []

    volume = neo4j.query(f"""
        MATCH()-[e:{functools.reduce(lambda a,b : f'{a}|{b}', relationtypes)}]->()
        return count(e)
    """, "Calculating Volume")[0][0]

    nr_vertices = neo4j.query(f"""
        MATCH (n)
        WHERE {functools.reduce(lambda a,b : f'n:{a} OR n:{b}', nodetypes)}
        return count(n)
    """)[0][0]

    results.append(["volume", volume, "edges"])
    results.append(["nr_vertices", nr_vertices, "vertices"])
    results.append(["size", volume + nr_vertices, "vertices + edges"])
    results.append(["fill", volume / (nr_vertices * nr_vertices), "edges/vertices^2"])

    csv.write(results, ["Statistic", "Value", "Unit"], "basic")
