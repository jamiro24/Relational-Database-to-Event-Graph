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
    "end_time": "2013-04-01"
}

incident_query = f"""
    select *
    from Incident
    where Open_Time between date("{config["start_time"]}") and date("{config["end_time"]}")
"""

activity_query = f"""
    select *
    from Incident_Activity
    where Incident_ID IN (
        select Incident_ID
        from Incident
        where Open_Time between date("{config["start_time"]}") and date("{config["end_time"]}")
    )
"""

interaction_query = f"""
    select *
    from Interaction
    where Interaction_ID IN (
        select Interaction_ID
        from Incident_Activity
        where Incident_ID IN (
            select Incident_ID
            from Incident
            where Open_Time between date("{config["start_time"]}") and date("{config["end_time"]}")
        )
    )
"""

change_query = f"""
    select * from Change
    where CI_Name_aff in (
        select CI_Name_aff
        from Interaction
        where Interaction_ID IN (
            select Interaction_ID
            from Incident_Activity
            where Incident_ID IN (
                select Incident_ID
                from Incident
                where Open_Time between date("{config["start_time"]}") and date("{config["end_time"]}")
            )
        )
    )
    or CI_Name_aff in (
        select CI_Name_aff
        from Incident
        where Open_Time between date("{config["start_time"]}") and date("{config["end_time"]}")
    )
    or CI_Name_aff in (
        select CI_Name_CBy
        from Incident
        where Open_Time between date("{config["start_time"]}") and date("{config["end_time"]}")
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
