import pandas as pd
import os
import sqlite3 as sql
from sqlite3 import OperationalError

# Read data from csv
change = pd.read_csv("csv/Detail Change.csv", sep=";")
incident = pd.read_csv("csv/Detail Incident.csv", sep=";")
incident = incident.loc[:, ~incident.columns.str.contains('^Unnamed')] # Remove unnamed columns from dataset
incident_activity = pd.read_csv("csv/Detail Incident Activity.csv", sep=";")
interaction = pd.read_csv("csv/Detail Interaction.csv", sep=";")

if os.path.exists("bpic14.db"):
    os.remove("bpic14.db")
conn = sql.connect("bpic14.db")
cursor = conn.cursor()

# Create tables
try:
    conn.execute('''
        CREATE TABLE Change (
            'ID' int PRIMARY KEY,
            'CI Name (aff)' text,
            'CI Type (aff)' text,
            'CI Subtype (aff)' text,
            'Service Component WBS (aff)' text,
            'Change ID' text,
            'Change Type' text,
            'Risk Assessment' text,
            'Emergency Change' text,
            'CAB-approval needed' text,
            'Planned Start' date,
            'Planned End' date,
            'Scheduled Downtime Start' date,
            'Scheduled Downtime End' date,
            'Actual Start' date,
            'Actual End' date,
            'Requested End Date' date,
            'Change record Open Time' date,
            'Change record Close Time' date,
            'Originated from' text,
            '# Related Interactions' int,
            '# Related Incidents' int
        )
    ''')
    print("Create `Change` table")
except OperationalError as e:
    print(e)

try:
    conn.execute('''
        CREATE TABLE Incident(
            'ID' int PRIMARY KEY,
            'CI Name (aff)' text,
            'CI Type (aff)' text,
            'CI Subtype (aff)' text,
            'Service Component WBS (aff)' text,
            'Incident ID' text,
            'Status' text,
            'Impact' text,
            'Urgency' text,
            'Priority' text,
            'Category' text,
            'KM number' text,
            'Alert Status' text,
            '# Reassignments' int,
            'Open Time' date,
            'Reopen Time' date,
            'Resolved Time' date,
            'Close Time' date,
            'Handle Time (Hours)' date,
            'Closure Code' text,
            '# Related Interactions' int,
            'Related Interaction' text,
            '# Related Incidents' int,
            '# Related Changes' int,
            'Related Change' text,
            'CI Name (CBy)' text,
            'CI Type (CBy)' text,
            'CI Subtype (CBy)' text,
            'ServiceComp WBS (CBy)' text
        )
    ''')
    print("Create `Incident` table")
except OperationalError as e:
    print(e)

try:
    conn.execute('''
        CREATE TABLE Interaction(
            'ID' int PRIMARY KEY,
            'CI Name (aff)' text,
            'CI Type (aff)' text,
            'CI Subtype (aff)' text,
            'Service Comp WBS (aff)' text,
            'Interaction ID' text,
            'Status' text,
            'Impact' int,
            'Urgency' text,
            'Priority' int,
            'Category' text,
            'KM number' text,
            'Open Time (First Touch)' date,
            'Close Time' date,
            'Closure Code' text,
            'First Call Resolution' text,
            'Handle Time (secs)' int,
            'Related Incident' text,
            FOREIGN KEY('Related Incident') REFERENCES Incident('Incident ID')
        )
    ''')
    print("Create `Interaction` table")
except OperationalError as e:
    print(e)


try:
    conn.execute('''
        CREATE TABLE 'Incident Activity'(
            'ID' int PRIMARY KEY,
            'Incident ID' text,
            'DateStamp' date,
            'IncidentActivity_Number' text,
            'IncidentActivity_Type' text,
            'Assignment Group' text,
            'KM number' text,
            'Interaction ID' text,
            FOREIGN KEY('Incident ID') REFERENCES Incident('Incident ID'),
            FOREIGN KEY('Interaction ID') REFERENCES Interaction('Interaction ID')
        )
    ''')
    print("Create `Incident Activity` table")
except OperationalError as e:
    print(e)


def is_null(val) -> bool:
    return pd.isnull(val)


# Insert values
def insert_value_sql(df: pd.DataFrame, types: list, table_name: str) -> str:
    v_str_all = f"INSERT INTO {table_name} VALUES"
    for row_nr, row in df.iterrows():
        v_str = f"\n({row_nr}"
        for i in range(0, df.shape[1]):
            v_str += ", "
            if is_null(row[i]):
                v_str += "null"
            elif types[i] == "text":
                v_str += f'\'{row[i]}\''
            elif types[i] == "int":
                v_str += f'{row[i]}'.split(".")[0]  # Get rid of decimals
            elif types[i] == "date":
                v_str += f'\'{row[i].replace("/","-")}\''
            else:
                print("unrecognized type")
        if row_nr < df.shape[0]-1:
            v_str += "),"
        else:
            v_str += ");"
        v_str_all += v_str
    return v_str_all


def insert(df: pd.DataFrame, name: str, types: list):
    insert_query = insert_value_sql(df, types, name)
    conn.execute(insert_query)
    print(f"inserted values into `{name}` table")


insert(change, "Change", ['text']*9+['date']*9+['text']+['int']*2)
insert(incident, "Incident", ['text']*12 + ['int'] + ['date']*5 + ['text', 'int']*2 + ['int'] + ['text']*5)
insert(interaction, "Interaction",  ['text']*6 + ['int', 'text', 'int'] + ['text']*2 + ['date']*2 + ['text']*2 + ['int', 'text'])
insert(incident_activity, "'Incident Activity'", ['text', 'date'] + ['text']*5)
