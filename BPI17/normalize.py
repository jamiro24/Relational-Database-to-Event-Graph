import pandas as pd
from pathlib import Path
import sqlite3 as sql
import os

import create_database_schema

work_dir: Path = Path(__file__).parents[0]
intermediary_dir = work_dir.joinpath("intermediary")
intermediary_dir.mkdir(parents=True, exist_ok=True)


def remove_illegal_chars(df: pd.DataFrame):
    df.columns = df.columns.str.replace(' ', '_')
    df.columns = df.columns.str.replace('case', 'ApplicationID')
    df.columns = df.columns.str.replace('event', 'Activity')
    df.columns = df.columns.str.replace('org:resource', 'resource')


def cleanup(df: pd.DataFrame):
    empty_cols = [col for col in df.columns if df[col].isnull().all()]
    # Drop these columns from the dataframe
    df.drop(empty_cols,
            axis=1,
            inplace=True)
    if 'EventOrigin' in df.keys().to_list():
        del df['EventOrigin']


print("Reading files")
log_frame = pd.read_csv('csv/BPI Challenge 2017.csv')
attributes_index: pd.Index = log_frame.keys()
offer_attributes = [
    'FirstWithdrawalAmount', 'NumberOfTerms', 'Accepted', 'MonthlyCost', 'Selected', 'CreditScore', 'OfferedAmount'
]
case_attributes = [
    'ApplicationType', 'case', 'RequestedAmount', 'LoanGoal', 'EventID'
]
event_attributes = [
    'Action', 'org:resource', 'event', 'EventOrigin', 'EventID', 'OfferID', 'startTime',
    'completeTime'
]
print("Normalizing")
application_filter = log_frame['EventOrigin'] == 'Application'
application_log_frame = log_frame[application_filter]
application_frame = application_log_frame[case_attributes].drop_duplicates()
application_frame = application_frame[application_frame['EventID'].str.startswith('Application_')]
del application_frame['EventID']
application_frame.to_csv(f'{intermediary_dir}/applications.csv', sep=',', index=False)

application_events_frame = application_log_frame[event_attributes]
application_events_frame.loc[:, 'ApplicationID'] = application_log_frame.loc[:, 'case']
application_events_frame.index.name = "ID"
application_events_frame.to_csv(f'{intermediary_dir}/application_events.csv', sep=',')
print("1/4")

offer_filter = log_frame['EventOrigin'] == 'Offer'
offer_log_frame = log_frame[offer_filter]
offer_log_frame.loc[offer_log_frame['OfferID'].isnull(), 'OfferID'] = offer_log_frame.loc[:, 'EventID']
offer_frame = offer_log_frame[case_attributes+offer_attributes].drop_duplicates()
offer_frame = offer_frame[offer_frame['EventID'].str.startswith('Offer_')]
offer_frame = offer_frame.rename(columns={'EventID': 'OfferID', 'id': 'ApplicationID'})
del offer_frame['LoanGoal']
del offer_frame['ApplicationType']
del offer_frame['RequestedAmount']
offer_frame.to_csv(f'{intermediary_dir}/offers.csv', sep=',', index=False)

offer_events_frame = offer_log_frame[event_attributes]
offer_events_frame.index.name = "ID"
offer_events_frame.to_csv(f'{intermediary_dir}/offer_events.csv', sep=',')
print("2/4")    

workflow_filter = log_frame['EventOrigin'] == 'Workflow'
workflow_log_frame = log_frame[workflow_filter]
workflow_frame = pd.DataFrame()
workflow_frame['WorkflowID'] = workflow_log_frame['case'].drop_duplicates()
workflow_frame.to_csv(f'{intermediary_dir}/workflows.csv', sep=',', index=False)

workflow_events_frame = workflow_log_frame[event_attributes]
workflow_events_frame.loc[:, 'WorkflowID'] = workflow_log_frame.loc[:, 'case']
workflow_events_frame.index.name = "ID"
workflow_events_frame.to_csv(f'{intermediary_dir}/workflow_events.csv', sep=',')
print("3/4")

resource_frame = log_frame[['org:resource']].drop_duplicates()
resource_frame.to_csv(f'{intermediary_dir}/resources.csv', sep=',', index=False)
print("4/4")

del resource_frame

if os.path.exists('BPI17_normalized.db'):
    os.remove("BPI17_normalized.db")
conn = sql.connect('BPI17_normalized.db')

print("Creating schema")

create_database_schema.create_schema(conn)

print("Importing to sql")
for file in work_dir.joinpath("intermediary").glob('**/*'):
    name, ext = os.path.splitext(file.name)
    frame = pd.read_csv(f'{file.parent}/{file.name}')
    remove_illegal_chars(frame)
    cleanup(frame)
    frame = frame
    frame.to_sql(con=conn, name=name, index=False, if_exists='append')

print("done")
