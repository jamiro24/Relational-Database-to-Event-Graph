import sqlite3 as sql
from typing import List, Dict, Set
import pandas as pd
import db_funcs_manual_transform as db_funcs
import os

def get_service_components(configuration_items: List[List[str]]):
    service_comps: Set[str] = set()
    for c_item in configuration_items:
        service_comps.add(c_item[0])
    return service_comps


def pivot_conf_items(configuration_items: List[List[str]]):
    pivoted: List[List[str]] = list()
    for i in range(4):
        pivoted.append(list())
    for c_item in configuration_items:
        for i in range(4):
            pivoted[i].append(c_item[i])
    return pivoted


input_path = "bpic14.sample.db"
output_path = "bpic14.sample_2_transformed.db"

if os.path.exists(output_path):
    os.remove(output_path)

input_conn = sql.connect(input_path)
output_conn = sql.connect(output_path)

service_component_sql_map: Dict[str, List[str]] = {
    'Change': ['Service_Component_WBS_aff'],
    'Incident': ['Service_Component_WBS_aff', 'ServiceComp_WBS_CBy'],
    'Interaction': ['Service_Comp_WBS_aff']
}

# Name and type are required to distinguish configuration items
configuration_item_sql_map: Dict[str, List[List[str]]] = {
    'Change': [["CI_Name_aff", "CI_Type_aff", "CI_Subtype_aff"]],
    'Interaction': [["CI_Name_aff", "CI_Type_aff", "CI_Subtype_aff"]],
    'Incident': [["CI_Name_aff", "CI_Type_aff", "CI_Subtype_aff"], ["CI_Name_CBy", "CI_Type_CBy", "CI_Subtype_CBy"]],
}

configuration_items: List[List[str]] = db_funcs.get_configuration_items(input_conn, service_component_sql_map, configuration_item_sql_map)

df_service_components = pd.DataFrame({
    "ID": list(get_service_components(configuration_items))
})

pivoted_configuration_items = pivot_conf_items(configuration_items)
del configuration_items
df_configuration_items = pd.DataFrame({
    "Service_Component": pivoted_configuration_items[0],
    "ID": pivoted_configuration_items[1],
    "Type": pivoted_configuration_items[2],
    "Subtype": pivoted_configuration_items[3]
})
del pivoted_configuration_items

db_funcs.create_db(output_conn)

df_service_components.to_sql('Service_Component', con=output_conn, if_exists='append', index=False)
df_configuration_items.to_sql('Configuration_Item', con=output_conn, if_exists='append', index=False)

df_change = pd.read_sql_query(sql="SELECT * FROM Change", con=input_conn)
del df_change['CI_Subtype_aff']
df_change.to_sql('Change', con=output_conn, if_exists='append', index=False)

df_interaction = pd.read_sql_query(sql="SELECT * FROM Interaction", con=input_conn)
del df_interaction['CI_Subtype_aff']
df_interaction.to_sql('Interaction', con=output_conn, if_exists='append', index=False)

df_incident = pd.read_sql_query(sql="SELECT * FROM Incident", con=input_conn)
del df_incident['CI_Subtype_aff']
del df_incident['CI_Subtype_CBy']
df_incident.to_sql('Incident', con=output_conn, if_exists='append', index=False)

df_incident_act = pd.read_sql_query(sql="SELECT * FROM Incident_Activity", con=input_conn)
df_incident_act.to_sql('Incident_Activity', con=output_conn, if_exists='append', index=False)
