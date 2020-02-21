from database.neo4j_connection import Neo4JConnection
from statistics import csv
from config.config import Config


def calculate(neo4j: Neo4JConnection, config: Config):

    results = []
    results_histogram = []

    for entitytype in config['entity'] + config['non_entity']:
        label = entitytype['label']

        result = __simple(neo4j, label)
        results.append([label] + result[0])
        result_histogram = __histogram(neo4j, label)

        for entree in result_histogram:
            results_histogram.append([label] + entree)

    csv.write(results, ['entity type', 'average', 'stdev', 'max', 'min'], 'df-path-length')
    results_histogram.sort(key=lambda a: a[1])
    results_histogram.sort(key=lambda a: a[0])
    csv.write(results_histogram, ['entity type', 'df_path_length', 'count'], 'df-path-length_histogram')


def __histogram(neo4j: Neo4JConnection, label: str):
    return neo4j.query(f"""
                MATCH (n:Entity {{EntityType: '{label}'}})
                OPTIONAL MATCH (n)<-[:E_EN]-(e:Event)
                WITH n, count(e) as nr_events
                unwind [nr_events,0] as path_length
                with n, max(path_length) as path_length
                RETURN path_length, count(n)
            """, f"Calculating histogram of lengths of df paths for entities with EntityType: {label}")


def __simple(neo4j: Neo4JConnection, label: str):
    return neo4j.query(f"""
            MATCH (n:Entity {{EntityType: '{label}'}})
            OPTIONAL MATCH (n)<-[:E_EN]-(e:Event)
            WITH n, count(e) as nr_events
            unwind [nr_events,0] as path_length
            with n, max(path_length) as path_length
            RETURN avg(path_length) as average,
            stdev(path_length) as stdev,
            max(path_length) as max,
            min(path_length) as min
        """, f"Calculating lengths of df paths for entities with EntityType: {label}")
