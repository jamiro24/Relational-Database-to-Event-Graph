import datetime
from sqlite3 import OperationalError

import pandas as pd


def create_db(conn):
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
                'Planned_Start' datetime,
                'Planned_End' datetime,
                'Scheduled_Downtime_Start' datetime,
                'Scheduled_Downtime_End' datetime,
                'Actual_Start' datetime,
                'Actual_End' datetime,
                'Requested_End_Date' datetime,
                'Change_record_Open_Time' datetime,
                'Change_record_Close_Time' datetime,
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
                'Open_Time' datetime,
                'Reopen_Time' datetime,
                'Resolved_Time' datetime,
                'Close_Time' datetime,
                'Handle_Time_Hours' text,
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
                'Open_Time_First_Touch' datetime,
                'Close_Time' datetime,
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
                date = row[i].replace('/', '-')
                try:
                    date = datetime.datetime.strptime(date, '%d-%m-%Y %H:%M').strftime('%d-%m-%Y %H:%M:00')
                except ValueError:
                    pass
                try:
                    date = datetime.datetime.strptime(date, '%d-%m-%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    pass
                v_str += f"\'{date}\'"
            else: # 26-12-2013 0:00
                print("unrecognized type")
        if row_nr < df.shape[0]-1:
            v_str += "),"
        else:
            v_str += ");"
        v_str_all += v_str
    return v_str_all


def insert(conn, df: pd.DataFrame, name: str, types: list):
    insert_query = insert_value_sql(df, types, name)
    conn.execute(insert_query)
    conn.commit()
    print(f"inserted values into `{name}` table")
