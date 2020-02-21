from database.neo4j_connection import Neo4JConnection
from statistics import csv
from config.config import Config


def calculate(neo4j: Neo4JConnection, config: Config):

    nodetypes = ["Event", "Common", "Entity", "Log"]
    simple_results = []
    histogram_results = []

    for nodetype in nodetypes:
        for dir in ["<", ">"]:
            direction = "in" if dir == "<" else "out"

            simple_result = __simple(neo4j, nodetype, dir)
            simple_results.append([f'{nodetype}', direction] + simple_result[0])
            histogram_result = __histogram(neo4j, nodetype, dir)
            for entree in histogram_result:
                histogram_results.append([f'{nodetype}', direction] + entree)

            if nodetype in ["Event", "Entity"]:
                for entity_type in config['entity'] + config['non_entity']:
                    simple_result = __simple(neo4j, nodetype, dir, entity_type['label'])
                    simple_results.append([f'{nodetype}: {entity_type["label"]}', direction] + simple_result[0])
                    histogram_result = __histogram(neo4j, nodetype, dir, entity_type['label'])
                    for entree in histogram_result:
                        histogram_results.append([f'{nodetype}: {entity_type["label"]}', direction] + entree)

    simple_results.sort(key=lambda a: a[0])
    histogram_results.sort(key=lambda a: a[2])
    histogram_results.sort(key=lambda a: a[1], reverse=True)
    histogram_results.sort(key=lambda a: a[0])

    csv.write(simple_results, ['node type', 'direction', 'average', 'stdev', 'max', 'min'], "degrees")
    csv.write(histogram_results, ['node type', 'direction', 'degree', 'count'], "degrees_histogram")


def __simple(neo4j: Neo4JConnection, nodetype: str, dir: str, entity_label: str = None):
    direction = "in" if dir == "<" else "out"

    match = f'MATCH (u:{nodetype}'
    message = f"Calculating {direction} degree of {nodetype} nodes"

    if entity_label is not None:
        match += f'{{EntityType: "{entity_label}"}}'
        message += f" with EntityType: {entity_label}"

    match += ')'

    return neo4j.query(f"""
                    {match}
                    RETURN avg(apoc.node.degree(u,'{dir}')) as average,
                    stdev(apoc.node.degree(u,'{dir}')) as stdev,
                    max(apoc.node.degree(u,'{dir}')) as max,
                    min(apoc.node.degree(u,'{dir}')) as min
                """, message)


def __histogram(neo4j: Neo4JConnection, nodetype: str, dir: str, entity_label: str = None):
    direction = "in" if dir == "<" else "out"

    match = f'MATCH (u:{nodetype}'
    message = f"Calculating histogram of {direction} degree of {nodetype} nodes"

    if entity_label is not None:
        match += f'{{EntityType: "{entity_label}"}}'
        message += f" with EntityType: {entity_label}"

    match += ')'

    return neo4j.query(f"""
                        {match}
                        RETURN apoc.node.degree(u,'{dir}'), count(u)
                    """, message)
