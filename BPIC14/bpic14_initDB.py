import pandas as pd
import os
import sqlite3 as sql
import datetime
import db_funcs

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

db_funcs.create_db(conn)
db_funcs.insert(conn, change, "Change", ['text']*9+['date']*9+['text']+['int']*2)
db_funcs.insert(conn, incident, "Incident", ['text']*12 + ['int'] + ['date']*4 + ['text'] + ['text', 'int']*2 + ['int'] + ['text']*5)
db_funcs.insert(conn, interaction, "Interaction",  ['text']*6 + ['int', 'text', 'int'] + ['text']*2 + ['date']*2 + ['text']*2 + ['int', 'text'])
db_funcs.insert(conn, incident_activity, "Incident_Activity", ['text', 'date'] + ['text']*5)
