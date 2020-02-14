from database.neo4j_connection import Neo4JConnection
from statistics import csv


def calculate(neo4j: Neo4JConnection):
    edges = neo4j.query("""
        match ()-[n]->() return type(n), count(n)
    """, "calculating counts per edge type")

    csv.write(edges, ["type", "count"], "counts-per-edge-type")

    nodes = neo4j.query("""
        match (n) return labels(n), count(n)
    """, "calculating counts per node type")

    csv.write(nodes, ["labels", "count"], "counts-per-node-type")


