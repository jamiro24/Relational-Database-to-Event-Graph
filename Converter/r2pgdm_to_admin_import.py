import pandas as pd
import sqlite3 as sql
import os

input_name = "BPI17_normalized"
input_path = f"{input_name}.db"

input_conn = sql.connect(input_path)

if not os.path.exists("admin"):
    os.mkdir("admin")

# region Transform edge table
# print('processing edges')
# edges = pd.read_sql(sql="select * from edge", con=input_conn, )
# edges = edges.rename(columns={
#     'id': 'edgeid',
#     'srcId': ':START_ID',
#     'tgtId': ':END_ID',
#     'label': ':TYPE'
# })
# edges = edges.drop_duplicates(subset=[':START_ID', ':END_ID'])  # We don't want duplicate edges in our transformation
# edges.to_csv("admin/edges.csv", sep=",", index=False)
# endregion

# region read metadata
meta = pd.read_sql(
    sql="""
        select distinct label, pkey
        from node
        left join property on node.id=property.id
        """,
    con=input_conn
)

table_names = meta['label'].drop_duplicates().to_list()
table_dict = {}
for name in table_names:
    meta_filter = meta['label'] == name
    table_dict[name] = meta[meta_filter].head()['pkey'].to_list()
# endregion

# region Translate nodes and properties
for table_name in table_dict.keys():
    print(f'processing nodes with label {table_name}')
    props = pd.read_sql(
        sql=f"""
        select node.id as ':ID', property.*
        from node
        left join property on node.id=property.id
        where label='{table_name}'
        """,
        con=input_conn
    )
    del props['id']
    props_pivoted = props.pivot(index=':ID', columns='pkey', values='pvalue')
    props_pivoted.reset_index(inplace=True)
    if pd.np.NaN in props_pivoted.columns:
        del props_pivoted[pd.np.NaN]
    props_pivoted[':LABEL'] = table_name
    props_pivoted.to_csv(f"admin/nodes-{table_name}.csv", sep=",", index=False)
# endregion

f = open("admin/import-command.txt", "w")

cmd = "bin/neo4j-admin import --relationships=\"import/edges.csv\""
for table_name in table_dict.keys():
    cmd += f" --nodes=\"import/nodes-{table_name}.csv\""
print(cmd)
f.write(cmd)
