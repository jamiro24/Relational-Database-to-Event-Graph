import sqlite3 as sql
from sqlite3 import OperationalError
from typing import List, Dict, Set
import pandas as pd


def create_db(conn):
    # Create tables
    try:
        conn.execute('''
            CREATE TABLE 'Service_Component'(
                'ID' text PRIMARY KEY 
            )
        ''')
        print("Create `Service_Component`")
    except OperationalError as e:
        print(e)

    try:
        conn.execute('''
            CREATE TABLE 'Configuration_Item'(
                'ID' text,
                'Name' text,
                'Type' text,
                'Subtype' text,
                'Service_Component' text,
                FOREIGN KEY ('Service_Component') REFERENCES Service_Component('ID'),
                PRIMARY KEY ('ID')
            )
        ''')
        print("Create `Configuration_Item`")
    except OperationalError as e:
        print(e)

    try:
        conn.execute('''
            CREATE TABLE 'Knowledge_Document'(
                'ID' text PRIMARY KEY 
            )
        ''')
        print("Create `Knowledge_Document`")
    except OperationalError as e:
        print(e)

    try:
        conn.execute('''
            CREATE TABLE 'Assignment_Group'(
                'ID' text PRIMARY KEY 
            )
        ''')
        print("Create `Assignment_Group`")
    except OperationalError as e:
        print(e)

    try:
        conn.execute('''
            CREATE TABLE Change (
                'ID' int PRIMARY KEY,
                'CI_ID_aff' text,
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
                'Nr_Related_Incidents' int,
                FOREIGN KEY('Service_Component_WBS_aff') REFERENCES Service_Component('ID'),
                FOREIGN KEY('CI_ID_aff') REFERENCES Configuration_Item('ID')
            )
        ''')
        print("Create `Change` table")
    except OperationalError as e:
        print(e)

    try:
        conn.execute('''
            CREATE TABLE Incident(
                'ID' int PRIMARY KEY,
                'CI_ID_aff' text,
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
                'CI_ID_CBy' text,
                'ServiceComp_WBS_CBy' text,
                FOREIGN KEY ('Service_Component_WBS_aff') REFERENCES Service_Component('ID'),
                FOREIGN KEY ('ServiceComp_WBS_CBy') REFERENCES Service_Component('ID'),
                FOREIGN KEY ('CI_ID_aff') REFERENCES Configuration_Item('ID'),
                FOREIGN KEY ('CI_ID_CBy') REFERENCES Configuration_Item('ID'),
                FOREIGN KEY ('KM_number') REFERENCES Knowledge_Document('ID')
            )
        ''')
        print("Create `Incident` table")
    except OperationalError as e:
        print(e)

    try:
        conn.execute('''
            CREATE TABLE Interaction(
                'ID' int PRIMARY KEY,
                'CI_ID_aff' text,
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
                FOREIGN KEY ('Related_Incident') REFERENCES Incident('Incident_ID'),
                FOREIGN KEY ('Service_Comp_WBS_aff') REFERENCES Service_Component('ID'),
                FOREIGN KEY ('CI_ID_aff') REFERENCES Configuration_Item('ID'),
                FOREIGN KEY ('KM_number') REFERENCES Knowledge_Document('ID')
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
                FOREIGN KEY ('Incident_ID') REFERENCES Incident('Incident_ID'),
                FOREIGN KEY ('Interaction_ID') REFERENCES Interaction('Interaction_ID'),
                FOREIGN KEY ('KM_number') REFERENCES Knowledge_Document('ID'),
                FOREIGN KEY ('Assignment_Group') REFERENCES Assignment_Group('ID')
            )
        ''')
        print("Create `Incident_Activity` table")
    except OperationalError as e:
        print(e)


def is_null(val) -> bool:
    return pd.isnull(val)


def get_configuration_items(conn: sql.Connection, sc_map: Dict[str, List[str]], ci_map: Dict[str, List[List[str]]]):
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT SC, CI, CI_Type, CI_Subtype
        FROM (
            SELECT Service_Component_WBS_aff as SC, CI_Name_aff as CI, CI_Type_aff as CI_Type, CI_Subtype_aff as CI_Subtype
            FROM Change
            UNION
            SELECT Service_Comp_WBS_aff as SC, CI_Name_aff as CI, CI_Type_aff as CI_Type, CI_Subtype_aff as CI_Subtype
            FROM Interaction
            UNION
            SELECT Service_Component_WBS_aff as SC, CI_Name_aff as CI, CI_Type_aff as CI_Type, CI_Subtype_aff as CI_Subtype
            FROM Incident	
            UNION
            SELECT ServiceComp_WBS_CBy as SC, CI_Name_CBy as CI, CI_Type_aff as CI_Type, CI_Subtype_CBy as CI_Subtype
            FROM Incident	
        )
    """)
    return cur.fetchall()
