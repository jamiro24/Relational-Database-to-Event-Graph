from database.neo4j_connection import Neo4JConnection
from statistics import csv
from config.config import Config
import functools
from os import path
import pandas as pd
import networkx as nx


def calculate(neo4j: Neo4JConnection):
    if not path.exists("statistics-csv/relationships.csv"):
        __retrieve_relationship_data(neo4j)
    else:
        print("Found existing relationship data, not retrieving new data")
        print("Delete the file 'statistics/relationships.csv' and rerun the diameter calculation to retrieve new data")

    diameters = []

    relationships = pd.read_csv('statistics-csv/relationships.csv')
    rel_filter = ~relationships['rel_type'].str.contains('-')
    relationships = relationships[rel_filter]

    # diameters.append(['none', __calc(relationships)])

    le_filter = ~(relationships['rel_type'].str.contains('L_E'))
    relationships = relationships[le_filter]
    diameters.append(['no L_E', __calc(relationships)])

    csv.write(diameters, ['restriction', 'diameter'], 'diameter')


def __calc(relationships: pd.DataFrame):
    sources = relationships['source_id'].to_list()
    targets = relationships['target_id'].to_list()
    relationships = [(sources[i], targets[i]) for i in range(0, len(sources))]

    g = nx.Graph()
    g.add_edges_from(relationships)

    diameter = -1

    if nx.is_connected(g):
        diameter = nx.diameter(g)
    else:
        components = nx.weakly_connected_components(g)

        for component in components:
            comp_diameter = nx.diameter(component)
            print(comp_diameter)
            diameter = max(diameter, comp_diameter)

    return diameter


def __retrieve_relationship_data(neo4j: Neo4JConnection):
    results = neo4j.query("""
        match (s)-[r]->(t)
        return ID(s) as sourceID, labels(s) as sourceLabels, ID(t) as targetID, labels(t) as targetLabels, type(r) as relationType
    """)

    for result in results:
        result[1] = result[1][0]
        result[3] = result[3][0]

    csv.write(results, ['source_id', 'source_label', 'target_id', 'target_label', 'rel_type'], 'relationships')
