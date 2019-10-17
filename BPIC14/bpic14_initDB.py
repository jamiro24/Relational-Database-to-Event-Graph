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
            'CI_Name_aff' text,
            'CI_Type_aff' text,
            'CI_Subtype_aff' text,
            'Service_Component_WBS_aff' text,
            'Change_ID' text,
            'Change_Type' text,
            'Risk_Assessment' text,
            'Emergency_Change' text,
            'CAB_approval_needed' text,
            'Planned_Start' date,
            'Planned_End' date,
            'Scheduled_Downtime_Start' date,
            'Scheduled_Downtime_End' date,
            'Actual_Start' date,
            'Actual_End' date,
            'Requested_End_Date' date,
            'Change_record_Open_Time' date,
            'Change_record_Close_Time' date,
            'Originated_from' text,
            'Nr_Related_Interactions' int,
            'Nr_Related_Incidents' int
        )
    ''')
    print("Create `Change` table")
except OperationalError as e:
    print(e)

try:
    conn.execute('''
        CREATE TABLE Incident(
            'ID' int PRIMARY KEY,
            'CI_Name_aff' text,
            'CI_Type_aff' text,
            'CI_Subtype_aff' text,
            'Service_Component_WBS_aff' text,
            'Incident_ID' text,
            'Status' text,
            'Impact' text,
            'Urgency' text,
            'Priority' text,
            'Category' text,
            'KM_number' text,
            'Alert_Status' text,
            'Nr_Reassignments' int,
            'Open_Time' date,
            'Reopen_Time' date,
            'Resolved_Time' date,
            'Close_Time' date,
            'Handle_Time_Hours' date,
            'Closure_Code' text,
            'Nr_Related_Interactions' int,
            'Related_Interaction' text,
            'Nr_Related_Incidents' int,
            'Nr_Related_Changes' int,
            'Related_Change' text,
            'CI_Name_CBy' text,
            'CI_Type_CBy' text,
            'CI_Subtype_CBy' text,
            'ServiceComp_WBS_CBy' text
        )
    ''')
    print("Create `Incident` table")
except OperationalError as e:
    print(e)

try:
    conn.execute('''
        CREATE TABLE Interaction(
            'ID' int PRIMARY KEY,
            'CI_Name_aff' text,
            'CI_Type_aff' text,
            'CI_Subtype_aff' text,
            'Service_Comp_WBS_aff' text,
            'Interaction_ID' text,
            'Status' text,
            'Impact' int,
            'Urgency' text,
            'Priority' int,
            'Category' text,
            'KM_number' text,
            'Open_Time_First_Touch' date,
            'Close_Time' date,
            'Closure_Code' text,
            'First_Call_Resolution' text,
            'Handle_Time_secs' int,
            'Related_Incident' text,
            FOREIGN KEY('Related_Incident') REFERENCES Incident('Incident_ID')
        )
    ''')
    print("Create `Interaction` table")
except OperationalError as e:
    print(e)


try:
    conn.execute('''
        CREATE TABLE 'Incident_Activity'(
            'ID' int PRIMARY KEY,
            'Incident_ID' text,
            'DateStamp' date,
            'IncidentActivity_Number' text,
            'IncidentActivity_Type' text,
            'Assignment_Group' text,
            'KM_number' text,
            'Interaction_ID' text,
            FOREIGN KEY('Incident_ID') REFERENCES Incident('Incident_ID'),
            FOREIGN KEY('Interaction_ID') REFERENCES Interaction('Interaction_ID')
        )
    ''')
    print("Create `Incident_Activity` table")
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
    conn.commit()
    print(f"inserted values into `{name}` table")


insert(change, "Change", ['text']*9+['date']*9+['text']+['int']*2)
insert(incident, "Incident", ['text']*12 + ['int'] + ['date']*5 + ['text', 'int']*2 + ['int'] + ['text']*5)
insert(interaction, "Interaction",  ['text']*6 + ['int', 'text', 'int'] + ['text']*2 + ['date']*2 + ['text']*2 + ['int', 'text'])
insert(incident_activity, "Incident_Activity", ['text', 'date'] + ['text']*5)
