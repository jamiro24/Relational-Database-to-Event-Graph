from database.neo4j_connection import Neo4JConnection
from statistics import csv
from config.config import Config
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd


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


def histograms_produce(csv_name: str, max_nr_buckets=10):

    if not os.path.exists('statistics-csv/images'):
        os.makedirs('statistics-csv/images')

    hist_frame = pd.read_csv(f'statistics-csv/{csv_name}.csv')
    split_hist_frames = []
    hist_frame['category'] = hist_frame['entity type']
    categories = hist_frame['category'].unique()

    for category in categories:
        category_filter = hist_frame['category'] == category
        filtered_frame = hist_frame[category_filter]
        split_hist_frames.append(filtered_frame)

    del hist_frame

    for split_hist_frame in split_hist_frames:
        category = split_hist_frame['category'].unique()[0]
        node_type = split_hist_frame['entity type'].unique()[0]

        max_degree_length = split_hist_frame['df_path_length'].max()
        min_degree_length = split_hist_frame['df_path_length'].min()

        diff_degree = max_degree_length - min_degree_length
        nr_buckets = min(diff_degree + 1, max_nr_buckets)

        buckets = np.arange(min_degree_length, max_degree_length, diff_degree / nr_buckets) if diff_degree else np.array([0])
        buckets = np.append(buckets, max_degree_length)
        buckets = np.floor(buckets)
        buckets = np.unique(buckets)

        if np.size(buckets) == 1:
            buckets = np.append(buckets, buckets[0] + 1)

        counts = split_hist_frame['count'].array
        df_path_length = split_hist_frame['df_path_length'].array

        hist_data = []
        for i in range(0, split_hist_frame.shape[0]):
            hist_data += counts[i] * [df_path_length[i]]
        plt.title(node_type)
        plt.ylabel('Number of occurrences')
        plt.xlabel(f'DF path length')
        plt.yscale('log', nonposy='clip')
        plt.xticks(buckets, rotation=15)
        plt.hist(hist_data, bins=buckets, color='grey')
        category = category.replace(': ', '-')
        plt.tight_layout()
        plt.savefig(f'statistics-csv/images/df-path-length-hist-{category}.png')
        plt.clf()
        plt.cla()
