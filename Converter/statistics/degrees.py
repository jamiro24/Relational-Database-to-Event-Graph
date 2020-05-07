from database.neo4j_connection import Neo4JConnection
from statistics import csv
from config.config import Config
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os


def calculate(neo4j: Neo4JConnection, config: Config):

    nodetypes = ["Event", "Common", "Entity", "Log"]
    simple_results = []
    histogram_results = []

    for nodetype in nodetypes:
        for dir in ["<", ">"]:
            direction = "in" if dir == "<" else "out"

            simple_result = __simple(neo4j, nodetype, dir)
            simple_results.append([f'{nodetype}', direction] + simple_result[0])
            histogram_result = __histogram_query_data(neo4j, nodetype, dir)
            for entree in histogram_result:
                histogram_results.append([f'{nodetype}', direction] + entree)

            if nodetype in ["Event", "Entity"]:
                for entity_type in config['entity']:
                    simple_result = __simple(neo4j, nodetype, dir, entity_type['label'])
                    simple_results.append([f'{nodetype}: {entity_type["label"]}', direction] + simple_result[0])
                    histogram_result = __histogram_query_data(neo4j, nodetype, dir, entity_type['label'])
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


def __histogram_query_data(neo4j: Neo4JConnection, nodetype: str, dir: str, entity_label: str = None):
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


def histograms_produce(csv_name: str, max_nr_buckets=10):

    if not os.path.exists('statistics-csv/images'):
        os.makedirs('statistics-csv/images')

    hist_frame = pd.read_csv(f'statistics-csv/{csv_name}.csv')
    split_hist_frames = []
    hist_frame['category'] = hist_frame['node type'] + ' ' + hist_frame['direction']
    categories = hist_frame['category'].unique()

    for category in categories:
        category_filter = hist_frame['category'] == category
        filtered_frame = hist_frame[category_filter]
        split_hist_frames.append(filtered_frame)

    del hist_frame

    for split_hist_frame in split_hist_frames:
        category = split_hist_frame['category'].unique()[0]
        node_type = split_hist_frame['node type'].unique()[0]
        direction = split_hist_frame['direction'].unique()[0]

        max_degree = split_hist_frame['degree'].max()
        min_degree = split_hist_frame['degree'].min()

        diff_degree = max_degree - min_degree
        nr_buckets = min(diff_degree + 1, max_nr_buckets)

        buckets = np.arange(min_degree, max_degree, diff_degree / nr_buckets) if diff_degree else np.array([0])
        buckets = np.append(buckets, max_degree)
        buckets = np.floor(buckets)
        buckets = np.unique(buckets)

        if np.size(buckets) == 1:
            buckets = np.append(buckets, buckets[0] + 1)

        counts = split_hist_frame['count'].array
        degrees = split_hist_frame['degree'].array

        hist_data = []
        for i in range(0, split_hist_frame.shape[0]):
            hist_data += counts[i] * [degrees[i]]
        plt.title(node_type)
        plt.ylabel('Number of occurrences')
        plt.xlabel(f'Node {direction} degree')
        plt.yscale('log', nonposy='clip')
        plt.xticks(buckets, rotation=15)
        plt.hist(hist_data, bins=buckets, color='grey')
        category = category.replace(': ', '-')
        plt.tight_layout()
        plt.savefig(f'statistics-csv/images/degree-hist-{category}.png')
        plt.clf()
        plt.cla()


