# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 14:02:29 2019

@author: 20175070
"""
#incidents
import pandas as pd
import time, csv
from py2neo import Graph, Node, Relationship
import random


def LoadLog(localFile):
    datasetList = []
    headerCSV = []
    i = 0
    with open(localFile) as f:
        reader = csv.reader(f)
        for row in reader:
            if (i==0):
                headerCSV = list(row)
                i +=1
            else:
               datasetList.append(row)
        
    log = pd.DataFrame(datasetList,columns=headerCSV)
    
    return headerCSV, log

def CreateEventQuery(logHeader, fileName, LogID = ""):
    query = f'USING PERIODIC COMMIT LOAD CSV WITH HEADERS FROM \"file:///{fileName}\" as line'
    brClose = '}'
    brOpen = '{'
    for col in logHeader:
        if col == 'idx':
            column = f'toInt(line.{col})'
        elif col in ['timestamp','start','end']:
            column = f'datetime(line.{col})'
        else:
            column = 'line.'+col
        newLine = ''
        if (logHeader.index(col) == 0 and LogID != ""):
            newLine = f' CREATE (e:Event {brOpen}Log: "{LogID}",{col}: {column},'
        elif (logHeader.index(col) == 0):
            newLine = f' CREATE (e:Event {brOpen}{col}: {column},'
        else:
            newLine = f' {col}: {column},'
        if (logHeader.index(col) == len(logHeader)-1):
            newLine = f' {col}: {column}{brClose})'
            
        query = query + newLine
    return query;


sample = True
createFile = True
path = 'C:\\Temp\\Import\\'
logs = []

cbClose = "}"
cbOpen = "{" 
Graph = Graph(password="1234")
Graph.delete_all()



### data prep

change = pd.read_csv(f'BPIC14/Detail_Change.csv', keep_default_na=True, sep=';')
incident = pd.read_csv(f'BPIC14/Detail_Incident.csv', keep_default_na=True, sep=';')
incidentDetail = pd.read_csv(f'BPIC14/Detail_Incident_Activity.csv', keep_default_na=True, sep=';')
interaction = pd.read_csv(f'BPIC14/Detail_Interaction.csv', keep_default_na=True, sep=';')




incident.drop(incident.iloc[:, 28:78], inplace=True, axis=1) #drop all empty columns
incident = incident.dropna(thresh=19) #drops all 'nan-only' rows


change.rename(columns={'Service Component WBS (aff)':'ServiceComponentAff',#sample by
                       'CI Name (aff)':'CINameAff',
                       'CI Type (aff)':'CITypeAff',
                       'CI Subtype (aff)':'CISubTypeAff',
                       'Change ID':'ChangeID',
                       'Change Type':'ChangeType',
                       'Risk Assessment':'RiskAssessment',
                       'Emergency Change':'EmergencyChange',
                       'CAB-approval needed':'CABApprovalNeeded',
                       'Planned Start':'PlannedStart',
                       'Planned End':'PlannedEnd',
                       'Scheduled Downtime Start':'ScheduledDowntimeStart',
                       'Scheduled Downtime End':'ScheduledDowntimeEnd',
                       'Actual Start':'ActualSTart',
                       'Actual End':'ActualEnd',
                       'Requested End Date':'RequestedEndDate',
                       'Change record Open Time':'start',#only 2 timestamps with no null values
                       'Change record Close Time':'end',#only 2 timestamps with no null values
                       'Originated from':'OriginatedFrom',
                       '# Related Interactions':'NoRelatedInteractions',
                       '# Related Incidents':'NoRelatedIncidents'
                       }, inplace=True)




incident.rename(columns={'Service Component WBS (aff)':'ServiceComponentAff',#sample by
                         'CI Name (aff)':'CINameAff',
                         'CI Type (aff)':'CITypeAff',
                         'CI Subtype (aff)':'CISubTypeAff',
                         'Incident ID':'IncidentID',
                         'KM number':'KMNo',
                         'Alert Status':'AlertStatus',
                         '# Reassignments':'NoReassignments',
                         'Open Time':'start', #only 2 timestamps with no null values
                         'Reopen Time':'ReopenTime',
                         'Resolved Time':'ResolvedTime',
                         'Close Time':'end', #only 2 timestamps with no null values
                         'Handle Time (Hours)':'HandleTime',
                         'Closure Code':'ClosureCode',
                         '# Related Interactions':'NoRelatedInteractions',
                         'Related Interaction':'RelatedInteraction',
                         '# Related Incidents':'NoRelatedIncidents',
                         '# Related Changes':'NoRelatedChanges',
                         'Related Change':'RelatedChange',
                         'CI Name (CBy)':'CINameCBy',
                         'CI Type (CBy)':'CITypeCBy',
                         'CI Subtype (CBy)':'CISubTypeCBy',
                         'ServiceComp WBS (CBy)':'ServiceComponentCBy'}, inplace=True)


incidentDetail.rename(columns={'Incident ID':'IncidentID',#sample by
                               'DateStamp':'timestamp', #timestamp
                               'IncidentActivity_Number':'IncidentActivityNumber',
                               'IncidentActivity_Type':'IncidentActivityType',
                               'Assignment Group':'AssignmentGroup',
                               'KM number':'KMNo',
                               'Interaction ID':'InteractionID'}, inplace=True)

interaction.rename(columns={'Service Comp WBS (aff)':'ServiceComponentAff',#sample by
                            'CI Name (aff)':'CINameAff',
                            'CI Type (aff)':'CITypeAff',
                            'CI Subtype (aff)':'CISubTypeAff',
                            'Interaction ID':'InteractionID',
                            'KM number':'KMNo',
                            'Open Time (First Touch)':'start', #start timestamp
                            'Close Time':'end', #end timestamp
                            'Closure Code':'ClosureCode',
                            'First Call Resolution':'FirstCallResolution',
                            'Handle Time (secs)':'HandleTime',
                            'Related Incident':'RelatedIncident'}, inplace=True)


#CHGentities = [['CINameAff','CI'],['ServiceComponentAff','ServiceComponent'],['ChangeID','Change']]
#INCentities = [['CINameAff','CI'],['ServiceComponentAff','ServiceComponent'],['IncidentID','Incident'],['RelatedInteraction','Interaction'],['KMNo','KM'],['RdelatedChange','Change'],['CINameCBy','CI']]
#INDentities = [['IncidentID','Incident'],['IncidentActivityNumber','IncidentActivity'],['KMNo','KM'],['AssignmentGroup','Group'],['InteractionID','Interaction']]
#INTentities = [['CINameAff','CI'],['ServiceComponentAff','ServiceComponent'],['InteractionID','Interaction'],['KMNo','KM'],['RelatedIncident','Incident']]
#change.isna().sum()
#incident.isna().sum()
#incidentDetail.isna().sum()
#interaction.isna().sum()
    
    
    
    
if sample:
    random.seed(1)
    change = change[change['ServiceComponentAff'].isin(random.sample(change.ServiceComponentAff.unique().tolist(),20))]
    incident = incident[incident['ServiceComponentAff'].isin(random.sample(incident.ServiceComponentAff.unique().tolist(),20))]
    incidentDetail = incidentDetail[incidentDetail['IncidentID'].isin(random.sample(incidentDetail.IncidentID.unique().tolist(),20))]
    interaction = interaction[interaction['ServiceComponentAff'].isin(random.sample(interaction.ServiceComponentAff.unique().tolist(),10))]

logID = 'CHG' #log prefix for change
entities = [['CINameAff','CI'],['ServiceComponentAff','ServiceComponent'],['ChangeID','Change']]
#for entity in entities:
#    columnName = entity[0]
#    change[columnName] = f'{logID}'+change[columnName].astype(str) #add prefix to entity ids 

change['start'] = pd.to_datetime(change['start'], format='%d-%m-%Y %H:%M')
change['start'] = change['start'].map(lambda x: x.strftime('%Y-%m-%dT%H:%M')+':00.000+0100')
change['end'] = pd.to_datetime(change['end'], format='%d-%m-%Y %H:%M')
change['end'] = change['end'].map(lambda x: x.strftime('%Y-%m-%dT%H:%M')+':00.000+0100')
change = change.reset_index(drop=True)

if sample:
    fileName = 'BPIC14Change_sample.csv'
else:
    fileName = 'BPIC14Change.csv'
if createFile:   
    change.to_csv(path+fileName, index=True, index_label="idx",na_rep="Unknown")

header, csvLog = LoadLog(path+fileName)
change = csvLog
logs.append([csvLog,logID,fileName,entities])

logID = 'INC' #log prefix for incident
entities = [['CINameAff','CI'],['ServiceComponentAff','ServiceComponent'],['IncidentID','Incident'],['RelatedInteraction','Interaction'],['KMNo','KM'],['RelatedChange','Change'],['CINameCBy','CI']]
incident = incident.replace(['#MULTIVALUE','#N/B'], 'Unknown')
#for entity in entities:
#    columnName = entity[0]
#    incident[columnName] = f'{logID}'+incident[columnName].astype(str) #add prefix to entity ids 

incident['start'] = pd.to_datetime(incident['start'], format='%d/%m/%Y %H:%M:%S')
incident['start'] = incident['start'].map(lambda x: x.strftime('%Y-%m-%dT%H:%M:%S')+'.000+0100')
incident['end'] = pd.to_datetime(incident['end'], format='%d/%m/%Y %H:%M:%S')
incident['end'] = incident['end'].map(lambda x: x.strftime('%Y-%m-%dT%H:%M:%S')+'.000+0100')
incident = incident.reset_index(drop=True)


if sample:
    fileName = 'BPIC14Incident_sample.csv'
else:
    fileName = 'BPIC14Incident.csv'
if createFile:   
    incident.to_csv(path+fileName, index=True, index_label="idx",na_rep="Unknown")
header, csvLog = LoadLog(path+fileName)
incident = csvLog
logs.append([csvLog,logID,fileName,entities])

logID = 'IND' #log prefix for incident detail
entities = [['IncidentID','Incident'],['IncidentActivityNumber','IncidentActivity'],['KMNo','KM'],['AssignmentGroup','Group'],['InteractionID','Interaction']]
#for entity in entities:
#    columnName = entity[0]
#    incidentDetail[columnName] = f'{logID}'+incidentDetail[columnName].astype(str) #add prefix to entity ids 

incidentDetail['timestamp'] = pd.to_datetime(incidentDetail['timestamp'], format='%d-%m-%Y %H:%M:%S')
incidentDetail['timestamp'] = incidentDetail['timestamp'].map(lambda x: x.strftime('%Y-%m-%dT%H:%M:%S')+'.000+0100')

incidentDetail = incidentDetail.reset_index(drop=True)


if sample:
    fileName = 'BPIC14IncidentDetail_sample.csv'
else:
    fileName = 'BPIC14IncidentDetail.csv'
if createFile:   
    incidentDetail.to_csv(path+fileName, index=True, index_label="idx",na_rep="Unknown")
header, csvLog = LoadLog(path+fileName)
incidentDetail = csvLog
logs.append([csvLog,logID,fileName,entities])

logID = 'INT' #log prefix for interaction
entities = [['CINameAff','CI'],['ServiceComponentAff','ServiceComponent'],['InteractionID','Interaction'],['KMNo','KM'],['RelatedIncident','Incident']]
#for entity in entities:
#    columnName = entity[0]
#    interaction[columnName] = f'{logID}'+interaction[columnName].astype(str) #add prefix to entity ids 

interaction['start'] = interaction['start'].astype('datetime64[ns]')
interaction['start'] = interaction['start'].map(lambda x: x.strftime('%Y-%m-%dT%H:%M:%S')+'.000+0100')
interaction['end'] = interaction['end'].astype('datetime64[ns]')
interaction['end'] = interaction['end'].map(lambda x: x.strftime('%Y-%m-%dT%H:%M:%S')+'.000+0100')
interaction = interaction.reset_index(drop=True)
interaction = interaction.replace(['#MULTIVALUE','#N/B'], 'Unknown')

if sample:
    fileName = 'BPIC14Interaction_sample.csv'
else:
    fileName = 'BPIC14Interaction.csv'
if createFile:
    interaction.to_csv(path+fileName, index=True, index_label="idx",na_rep="Unknown")
header, csvLog = LoadLog(path+fileName)
interaction = csvLog
logs.append([csvLog,logID,fileName,entities])

#logs = [[change,'CHG'], [incident,'INC'], [incidentDetail,'IND'], [interaction,'INT']]
#
#logs = [change, incident, incidentDetail, interaction]


Graph.run('CREATE CONSTRAINT ON (e:Event) ASSERT e.ID IS UNIQUE;') #for implementation only (not required by schema or patterns)
Graph.run('CREATE CONSTRAINT ON (en:Entity) ASSERT en.uID IS UNIQUE;') #required by core pattern
Graph.run('CREATE CONSTRAINT ON (l:Log) ASSERT l.ID IS UNIQUE;') #required by core pattern


for log in logs:
    print("Log: "+log[1]+"#######################")
    qCreateEvents = CreateEventQuery(list(log[0]), log[2], log[1]) #generate query to create all events with all log columns as properties
    Graph.run(qCreateEvents)
    
    
    logID = log[1]
    
    #create log node and :L_E relationships
    Graph.create(Node("Log", ID=f'{logID}'))
    Graph.run(f'MATCH (e:Event {cbOpen}Log: "{logID}"{cbClose}) MATCH (l:Log {cbOpen}ID: "{logID}"{cbClose}) CREATE (l)-[:L_E]->(e)')
    
    q = f'MATCH (e:Event {cbOpen}Log: "{logID}"{cbClose}) MATCH (l:Log {cbOpen}ID: "{logID}"{cbClose}) CREATE (l)-[:L_E]->(e)'
    
    for entity in log[3]: #per entity
    
        start = time.time()
          
        
        #create entity nodes 
        query=f'''MATCH (e:Event) <-[:L_E]-(l:Log) WHERE l.ID = "{logID}" 
        WITH e.{entity[0]} AS id  
        MERGE (en:Entity {cbOpen}ID:("{logID}"+toString(id)) {cbClose})
        ON CREATE SET en.IDraw  = id, en.uID = "{entity[1]}"+"{logID}"+toString(id), en.Log = "{logID}", en.EntityType = "{entity[1]}" '''
        Graph.run(query)
        print(f'{entity[1]} entity nodes done')

        
        end = time.time()
        print(f"Entity node creation for {entity[1]} took: "+str((end - start))+" seconds.")
        start = time.time()    
        
        #create :E_EN relationships
        query=f'MATCH (e:Event {cbOpen}Log: "{logID}"{cbClose}), (n:Entity {cbOpen}EntityType: "{entity[1]}"{cbClose}) WHERE e.{entity[0]} = n.IDraw MERGE (e)-[:E_EN {cbOpen}EntityType: "{entity[1]}"{cbClose}]->(n)'
        Graph.run(query)
        
        end = time.time()
        print(f":E_EN creation for {entity[1]} nodes took: "+str((end - start))+" seconds.")
    
        start2 = time.time()
        #get all events per entity and add entity-specific index as property
        query = f'MATCH p = (ev:Event {cbOpen}Log: "{logID}"{cbClose}) -[:E_EN]-> (en:Entity {cbOpen}EntityType: "{entity[1]}"{cbClose}) RETURN ev ORDER BY ev.{entity[0]}, ev.idx'         
        output = Graph.run(query).data()
        entityIdx = 0    
        propertyName = f'{entity[1]}_idx'
        for node in output:
            node['ev'][propertyName] = entityIdx
            Graph.push(node['ev'])
            entityIdx += 1   
        
        end2 = time.time()
        print(f"Indexing {entity[1]} nodes took: "+str((end2 - start2))+" seconds.")         
        
        start = time.time()  
        #create DF relations       
        query = f'''MATCH (l:Log)-[:L_E]->(e1:Event) -[:E_EN]-> (ent:Entity {cbOpen}EntityType: "{entity[1]}"{cbClose}) <-[:E_EN]- (e2:Event)<-[:L_E]-(l:Log)
        WHERE e2.{propertyName} - e1.{propertyName} = 1 AND l.ID = "{logID}"
        MERGE (e2) -[df:DF]-> (e1)
        ON CREATE SET df.EntityTypes = ["{entity[1]}"]
        ON MATCH SET df.EntityTypes = CASE WHEN "{entity[1]}" IN df.EntityTypes THEN df.EntityTypes ELSE df.EntityTypes + "{entity[1]}" END
        '''
        #CREATE (e2) -[:DF {cbOpen}EntityType: "{entity[1]}",duration: duration.between(e2.timestamp, e1.timestamp){cbClose}]-> (e1)
        Graph.run(query)
        end = time.time()
        print(f":DF creation for {entity[1]} events took: "+str((end - start))+" seconds.")
    
