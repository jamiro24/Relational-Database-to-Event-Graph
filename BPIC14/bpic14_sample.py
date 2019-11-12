import os
import sqlite3 as sql
import db_funcs
import pandas as pd

# Takes a sample of an existing bpic14 db
# Takes all incidents with an 'Open_Time' between two set dates
# Takes all incident activities with incident id in the list of incidents
# Takes all interactions with interaction id in the list of incident activities
# Takes all changes with CI in the list of CIs in incident aff, cby and interaction aff


if os.path.exists("bpic14.sample.db"):
    os.remove("bpic14.sample.db")

input_conn = sql.connect("bpic14.db")
output_conn = sql.connect("bpic14.sample.db")

config = {
    "start_time": "2013-01-01",
    "end_time": "2013-02-01"
}

incident_query = f"""
    SELECT *
    FROM Incident
    WHERE Incident_ID IN (
        SELECT Related_Incident
        FROM Interaction
        WHERE Service_Comp_WBS_aff IN (
            select DISTINCT Service_Component_WBS_aff
            FROM Change
            LIMIT 5
        )
    ) OR Incident_ID IN (
        SELECT Incident_ID
        FROM Incident_Activity
        WHERE Interaction_ID IN (
            SELECT Interaction_ID
                FROM Interaction
                WHERE Service_Comp_WBS_aff IN (
                    select DISTINCT Service_Component_WBS_aff
                    FROM Change
                    LIMIT 5
            )
        )
    )
"""

activity_query = f"""
    SELECT *
    FROM Incident_Activity
    WHERE Interaction_ID IN (
        SELECT Interaction_ID
            FROM Interaction
            WHERE Service_Comp_WBS_aff IN (
                select DISTINCT Service_Component_WBS_aff
                FROM Change
                LIMIT 5
        )
    )
"""

interaction_query = f"""
    SELECT *
    FROM Interaction
    WHERE Service_Comp_WBS_aff IN (
        select DISTINCT Service_Component_WBS_aff
        FROM Change
        LIMIT 5
    )
"""

change_query = f"""
    SELECT *
    FROM Change
    WHERE Service_Component_WBS_aff IN (
        select DISTINCT Service_Component_WBS_aff
        FROM Change
        LIMIT 5
    )
"""

db_funcs.create_db(output_conn)
incident = pd.read_sql(incident_query, input_conn)
del incident["ID"]
incident_activity = pd.read_sql(activity_query, input_conn)
del incident_activity["ID"]
interaction = pd.read_sql(interaction_query, input_conn)
del interaction["ID"]
change = pd.read_sql(change_query, input_conn)
del change["ID"]

print("Retrieved data")

db_funcs.create_db(output_conn)
db_funcs.insert(output_conn, change, "Change", ['text']*9+['date']*9+['text']+['int']*2)
db_funcs.insert(output_conn, incident, "Incident", ['text']*12 + ['int'] + ['date']*4 + ['text'] + ['text', 'int']*2 + ['int'] + ['text']*5)
db_funcs.insert(output_conn, interaction, "Interaction",  ['text']*6 + ['int', 'text', 'int'] + ['text']*2 + ['date']*2 + ['text']*2 + ['int', 'text'])
db_funcs.insert(output_conn, incident_activity, "Incident_Activity", ['text', 'date'] + ['text']*5)
