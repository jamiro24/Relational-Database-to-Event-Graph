from neo4j import GraphDatabase
from neobolt.exceptions import ServiceUnavailable
import time
# Need correct neo4j package versions:
# pip install --force-reinstall neo4j==1.7.2 neobolt==1.7.9 neotime==1.7.4

# Database Credentials
uri = "bolt://127.0.0.1:11006"
userName = "neo4j"
password = "1234"

start_time =round(time.monotonic() * 1000)


def query(q):
    driver = GraphDatabase.driver(uri, auth=(userName, password))
    print(f'Executing query:\n{q}\n')
    try:
        executed_query = driver.session().run(q)
        results = executed_query.values()  # wait for results to make sure queries are executed one at a time
        driver.close()
        return results
    except ServiceUnavailable:
        print("Connection dropped, retrying")
        query(q)


def cleanup_previous():
    node_types = ['Entity', 'Event', 'Log', 'Common', 'TempEvent']
    for node_type in node_types:
        query(f"""
            MATCH (n:{node_type})
            OPTIONAL MATCH (n)-[r]-()
            DELETE n,r
        """)


def cleanup_temp():
    query("""
    MATCH (e:TempEvent)
    DELETE e
    """)


answer = ""
while answer not in ["y", "n"]:
    answer = input(f"This will delete any existing event graph . Is this okay [Y/N]? ").lower()
if answer != "y":
    exit(1)
# begin
cleanup_previous()

query("""
CREATE INDEX ON :Entity(EntityType)
""")

query("""
CREATE INDEX ON :Event(start)
""")

query("""
CREATE INDEX ON :TempEvent(originID)
""")

# region Create entity nodes
query("""
MATCH (n:Change)
WITH DISTINCT n.Change_ID as id
CALL apoc.create.node(['Entity'], {EntityType:'Change', ID:'BPI14'+id, IDraw:id, Log:'BPI14', uID:'ChangeBPI14'+id}) yield node
RETURN node
""")

query("""
MATCH (n:Incident)
WITH DISTINCT n.Incident_ID as id
CALL apoc.create.node(['Entity'], {EntityType:'Incident', ID:'BPI14'+id, IDraw:id, Log:'BPI14', uID:'IncidentBPI14'+id}) yield node
RETURN node
""")

query("""
MATCH (n:Interaction)
WITH DISTINCT n.Interaction_ID as id
CALL apoc.create.node(['Entity'], {EntityType:'Interaction', ID:'BPI14'+id, IDraw:id, Log:'BPI14', uID:'InteractionBPI14'+id}) yield node
RETURN node
""")

query("""
MATCH (n:Incident_Activity)
WITH DISTINCT n.IncidentActivity_Number as id
CALL apoc.create.node(['Entity'], {EntityType:'Incident_Activity', ID:'BPI14'+id, IDraw:id, Log:'BPI14', uID:'Incident_ActivityBPI14'+id}) yield node
RETURN node
""")

query("""
MATCH (n:Knowledge_Document)
WITH DISTINCT n.ID as id
CALL apoc.create.node(['Entity'], {EntityType:'Knowledge_Document', ID:'BPI14'+id, IDraw:id, Log:'BPI14', uID:'Knowledge_DocumentBPI14'+id}) yield node
RETURN node
""")

query("""
MATCH (n:Assignment_Group)
WITH DISTINCT n.ID as id
CALL apoc.create.node(['Entity'], {EntityType:'Assignment_Group', ID:'BPI14'+id, IDraw:id, Log:'BPI14', uID:'Assignment_GroupBPI14'+id}) yield node
RETURN node
""")

query("""
MATCH (n:Configuration_Item)
WITH DISTINCT n.Name as id
CALL apoc.create.node(['Entity'], {EntityType:'Configuration_Item', ID:'BPI14'+id, IDraw:id, Log:'BPI14', uID:'Configuration_ItemBPI14'+id}) yield node
RETURN node
""")

query("""
MATCH (n:Service_Component)
WITH DISTINCT n.ID as id
CALL apoc.create.node(['Entity'], {EntityType:'Service_Component', ID:'BPI14'+id, IDraw:id, Log:'BPI14', uID:'Service_ComponentBPI14'+id}) yield node
RETURN node
""")
# endregion

# region Create event nodes
query("""
// Create temp event nodes for change and related entities
// We merge nodes in case the entity is related to to the same
// entity multiple times

MATCH (c:Change)
MERGE (n:TempEvent {originID: ID(c), commonID: ID(c)})
ON CREATE SET n+=c
ON CREATE SET n.EntityType="Change"
ON CREATE SET n.IDraw=c.Change_ID

Return c
""")

query("""
// Create temp event nodes for change and related entities
// We merge nodes in case the entity is related to to the same
// entity multiple times

MATCH (c:Change)-[]->(sc:Service_Component)
MERGE (n:TempEvent {originID: ID(sc), commonID: ID(c)})
ON CREATE SET n+=sc
ON CREATE SET n.EntityType="Service_Component"
ON CREATE SET n.IDraw=sc.ID

Return c
""")

query("""
// Create temp event nodes for change and related entities
// We merge nodes in case the entity is related to to the same
// entity multiple times

MATCH (c:Change)-[]->(ci:Configuration_Item)
MERGE (n:TempEvent {originID: ID(ci), commonID: ID(c)})
ON CREATE SET n+=ci
ON CREATE SET n.EntityType="Configuration_Item"
ON CREATE SET n.IDraw=ci.Name

Return c
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Change'})
WHERE 'Actual_Start' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Change_Actual_Start'
SET event.Start = ent.Actual_Start
SET event.End = ent.Actual_Start

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Change'})
WHERE 'Actual_End' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Change_Actual_End'
SET event.Start = ent.Actual_End
SET event.End = ent.Actual_End

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Change'})
WHERE 'Planned_Start' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Change_Planned_Start'
SET event.Start = ent.Planned_Start
SET event.End = ent.Planned_Start

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Change'})
WHERE 'Planned_End' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Change_Planned_End'
SET event.Start = ent.Planned_End
SET event.End = ent.Planned_End

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Change'})
WHERE 'Scheduled_Downtime_Start' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Change_Scheduled_Downtime_Start'
SET event.Start = ent.Scheduled_Downtime_Start
SET event.End = ent.Scheduled_Downtime_Start

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Change'})
WHERE 'Scheduled_Downtime_End' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Change_Scheduled_Downtime_End'
SET event.Start = ent.Scheduled_Downtime_End
SET event.End = ent.Scheduled_Downtime_End

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Change'})
WHERE 'Requested_End_Date' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Change_Requested_End_Date'
SET event.Start = ent.Requested_End_Date
SET event.End = ent.Requested_End_Date

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Change'})
WHERE 'Change_record_Open_Time' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Change_record_Open_Time'
SET event.Start = ent.Change_record_Open_Time
SET event.End = ent.Change_record_Open_Time

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Change'})
WHERE 'Change_record_Close_Time' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Change_record_Close_Time'
SET event.Start = ent.Change_record_Close_Time
SET event.End = ent.Change_record_Close_Time

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

cleanup_temp()

query("""
// Create temp event nodes for change and related entities
// We merge nodes in case the entity is related to to the same
// entity multiple times
MATCH (i:Incident)

MERGE (n:TempEvent {originID: ID(i), commonID: ID(i)})
ON CREATE SET n+=i
ON CREATE SET n.EntityType="Incident"
ON CREATE SET n.IDraw=i.Incident_ID

Return i
""")

query("""
// Create temp event nodes for change and related entities
// We merge nodes in case the entity is related to to the same
// entity multiple times
MATCH (i:Incident)-[]->(sc:Service_Component)

MERGE (n:TempEvent {originID: ID(sc), commonID: ID(i)})
ON CREATE SET n+=sc
ON CREATE SET n.EntityType="Service_Component"
ON CREATE SET n.IDraw=sc.ID

Return i
""")

query("""
// Create temp event nodes for change and related entities
// We merge nodes in case the entity is related to to the same
// entity multiple times
MATCH (i:Incident)-[]->(ci:Configuration_Item)

MERGE (n:TempEvent {originID: ID(ci), commonID: ID(i)})
ON CREATE SET n+=ci
ON CREATE SET n.EntityType="Configuration_Item"
ON CREATE SET n.IDraw=ci.Name

Return i
""")

query("""
// Create temp event nodes for change and related entities
// We merge nodes in case the entity is related to to the same
// entity multiple times
MATCH (i:Incident)-[]->(kd:Knowledge_Document)

MERGE (n:TempEvent {originID: ID(kd), commonID: ID(i)})
ON CREATE SET n+=kd
ON CREATE SET n.EntityType="Knowledge_Document"
ON CREATE SET n.IDraw=kd.ID

Return i
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Incident'})
WHERE 'Open_Time' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Incident_Open_Time'
SET event.Start = ent.Open_Time
SET event.End = ent.Open_Time

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Incident'})
WHERE 'Reopen_Time' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Incident_Reopen_Time'
SET event.Start = ent.Reopen_Time
SET event.End = ent.Reopen_Time

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Incident'})
WHERE 'Resolved_Time' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Incident_Resolved_Time'
SET event.Start = ent.Resolved_Time
SET event.End = ent.Resolved_Time

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Incident'})
WHERE 'Close_Time' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Incident_Close_Time'
SET event.Start = ent.Close_Time
SET event.End = ent.Close_Time

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

cleanup_temp()

query("""
// Create temp event nodes for change and related entities
// We merge nodes in case the entity is related to to the same
// entity multiple times
MATCH (i:Interaction)

MERGE (n:TempEvent {originID: ID(i), commonID: ID(i)})
ON CREATE SET n+=i
ON CREATE SET n.EntityType="Interaction"
ON CREATE SET n.IDraw=i.Interaction_ID

return i
""")

query("""
// Create temp event nodes for change and related entities
// We merge nodes in case the entity is related to to the same
// entity multiple times
MATCH (i:Interaction)-[]->(sc:Service_Component)

MERGE (n:TempEvent {originID: ID(sc), commonID: ID(i)})
ON CREATE SET n+=sc
ON CREATE SET n.EntityType="Service_Component"
ON CREATE SET n.IDraw=sc.ID

return i
""")

query("""
// Create temp event nodes for change and related entities
// We merge nodes in case the entity is related to to the same
// entity multiple times
MATCH (i:Interaction)-[]->(ci:Configuration_Item)

MERGE (n:TempEvent {originID: ID(ci), commonID: ID(i)})
ON CREATE SET n+=ci
ON CREATE SET n.EntityType="Configuration_Item"
ON CREATE SET n.IDraw=ci.Name

return i
""")

query("""
// Create temp event nodes for change and related entities
// We merge nodes in case the entity is related to to the same
// entity multiple times
MATCH (i:Interaction)-[]->(kd:Knowledge_Document)

MERGE (n:TempEvent {originID: ID(kd), commonID: ID(i)})
ON CREATE SET n+=kd
ON CREATE SET n.EntityType="Knowledge_Document"
ON CREATE SET n.IDraw=kd.ID

return i
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Interaction'})
WHERE 'Open_Time_First_Touch' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Interaction_Open_Time_First_Touch'
SET event.Start = ent.Open_Time_First_Touch
SET event.End = ent.Open_Time_First_Touch

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Interaction'})
WHERE 'Close_Time' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Interaction_Close_Time'
SET event.Start = ent.Close_Time
SET event.End = ent.Close_Time

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

cleanup_temp()

query("""
// Find entities related to Incident Activity
MATCH (i:Incident_Activity)

MERGE (n:TempEvent {originID: ID(i), commonID: ID(i)})
ON CREATE SET n+=i
ON CREATE SET n.EntityType="Incident_Activity"
ON CREATE SET n.IDraw=i.IncidentActivity_Number

return i
""")

query("""
// Find entities related to Incident Activity
MATCH (i:Incident_Activity)-[]->(kd:Knowledge_Document)

MERGE (n:TempEvent {originID: ID(kd), commonID: ID(i)})
ON CREATE SET n+=kd
ON CREATE SET n.EntityType="Knowledge_Document"
ON CREATE SET n.IDraw=kd.ID

return i
""")

query("""
// Find entities related to Incident Activity
MATCH (i:Incident_Activity)-[]->(ag:Assignment_Group)

MERGE (n:TempEvent {originID: ID(ag), commonID: ID(i)})
ON CREATE SET n+=ag
ON CREATE SET n.EntityType="Assignment_Group"
ON CREATE SET n.IDraw=ag.ID

return i
""")

query("""
// Find entities related to Incident Activity
MATCH (i:Incident_Activity)-[]->(inc:Incident)

MERGE (n:TempEvent {originID: ID(inc), commonID: ID(i)})
ON CREATE SET n+=inc
ON CREATE SET n.EntityType="Incident"
ON CREATE SET n.IDraw=inc.Incident_ID

return i
""")

query("""
// Find entities related to Incident Activity
MATCH (i:Incident_Activity)-[]->(int:Interaction)

MERGE (n:TempEvent {originID: ID(int), commonID: ID(i)})
ON CREATE SET n+=int
ON CREATE SET n.EntityType="Interaction"
ON CREATE SET n.IDraw=int.Interaction_ID

return i
""")

query("""
// Find Incident TempEvents that should generate this event
MATCH (ent:TempEvent {EntityType:'Incident_Activity'})
WHERE 'DateStamp' in keys(ent)

// Find other matching TempEvent
MATCH (t:TempEvent {commonID: ent.commonID})
WITH ent, t

CREATE (event:Event)
SET event = t
SET event.Activity = 'Incident_Activity_'+ent.IncidentActivity_Type
SET event.Start = ent.DateStamp
SET event.End = ent.DateStamp

WITH ent, collect(event) as events

CREATE (co:Common)

WITH co, events
UNWIND events as event
WITH co, event

// Create relations between events and common nodes
CREATE (event)-[ec:E_C {entityType: event.entityType}]->(co)

return event, co, ec
""")

cleanup_temp()
# endregion

query("""
MATCH (ev:Event)
MATCH (en:Entity {IDraw: ev.IDraw, EntityType:ev.EntityType})
CREATE (ev)-[r:E_EN]->(en)
SET r.EntityType = en.EntityType
return null
""")

query("""
MATCH (n:Entity)
MATCH (n)-[]-(ev)

WITH n, ev as nodes ORDER BY ev.Start, ID(ev)
WITH n, collect(nodes) as nodeList
WITH n, apoc.coll.pairsMin(nodeList) as pairs
UNWIND pairs as pair
WITH n, pair[0] as first, pair[1] as second

CREATE (first)-[df:DF]->(second)
SET df.EntityType = n.EntityType
SET df.EntityId = n.ID
RETURN null
""")

# Create log node
query("""
CREATE (l:Log {ID: 'BPI14'})
WITH l
Match (e:Event)
CREATE (l)-[r:L_E]->(e)
RETURN *
""")

end_time = round(time.monotonic() * 1000)
print(f'Finished in {(end_time-start_time)/60000} Minutes')
