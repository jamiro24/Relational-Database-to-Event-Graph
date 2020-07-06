# Relational-Database-to-Event-Graph
Facilitates the Semi-Automatic transformation of relational databases into graph database.


This repository consists of three folders. BPI17 and BPIC14Manual contain python files that perform a manually built transformation of a Neo4J database containing a generic graph representation of a relational database (Use [This Repo](https://github.com/jamiro24/R2PG-DM) to transform your relational database into such a generic representation). 


The 'Converter' folder contains the semi-automatic approach to this problem. In order to use this converter you need to provide it with a config file (`config.json`) for the specific database you want to transform. The provided `config.json` file is set up to transform the BPI 17 dataset. After creating such a config file, the program can be started by running `main.py`

This transformation is meant to be used with Neo4j 3.5.15. Neo4J 4.0 and higher use a new method to connect to databases, which has not been implemented, and as such still needs to be implemented in `/Converter/database/neo4j_connection.py`.


Below you can download two Neo4j Database dumps. The nodes in these dump are named differently than what the converter output, due to a naming change late in the project.

BPI 14 dump: https://mega.nz/file/hIcnGSyI#-DhjT6qiv4GgrqO41V6zD0ETH_EJwvvoazwiPW7iOq0
BPI 17 dump: https://mega.nz/file/gMcgDCwD#QYkdiTNXRKmSJiNgLcLWVW_LLpjBDLx3iByfE0r_9M4
