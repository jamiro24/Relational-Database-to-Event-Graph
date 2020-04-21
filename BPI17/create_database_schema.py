import sqlite3


def create_schema(conn:sqlite3.Connection):

    conn.execute("""
        CREATE TABLE "resources" (
            "resource"	TEXT,
            PRIMARY KEY("resource")
        );
    """)

    conn.execute("""
        CREATE TABLE "applications" (
            "ApplicationType"	TEXT,
            "ApplicationID"	TEXT,
            "RequestedAmount"	REAL,
            "LoanGoal"	TEXT,
            PRIMARY KEY("ApplicationID")
        );
    """)

    conn.execute("""
        CREATE TABLE "application_events" (
    	    "Action"	TEXT,
    	    "resource"	TEXT,
    	    "Activity"	TEXT,
    	    "EventID"	TEXT,
    	    "OfferID"	TEXT,
    	    "startTime"	TEXT,
    	    "completeTime"	TEXT,
    	    "ApplicationID"	TEXT,
    	    FOREIGN KEY("ApplicationID") REFERENCES "applications"("ApplicationID"),
    	    FOREIGN KEY("resource") REFERENCES "resources"("resource"),
    	    PRIMARY KEY("EventID")
        );
    """)

    conn.execute("""
        CREATE TABLE "offers" (
            "ApplicationID"	TEXT,
            "OfferID"	TEXT,
            "FirstWithdrawalAmount"	REAL,
            "NumberOfTerms"	REAL,
            "Accepted"	INTEGER,
            "MonthlyCost"	REAL,
            "Selected"	INTEGER,
            "CreditScore"	REAL,
            "OfferedAmount"	REAL,
            PRIMARY KEY("OfferID"),
            FOREIGN KEY("ApplicationID") REFERENCES "applications"("ApplicationID")
        );
    """)

    conn.execute("""
        CREATE TABLE "offer_events" (
            "Action"	TEXT,
            "resource"	TEXT,
            "Activity"	TEXT,
            "EventID"	TEXT,
            "OfferID"	TEXT,
            "startTime"	TEXT,
            "completeTime"	TEXT,
            FOREIGN KEY("OfferID") REFERENCES "offers"("OfferID"),
            PRIMARY KEY("EventID"),
            FOREIGN KEY("resource") REFERENCES "resources"("resource")
        );
    """)

    conn.execute("""
        CREATE TABLE "workflows" (
            "WorkflowID"	TEXT,
            PRIMARY KEY("WorkflowID"),
            FOREIGN KEY("WorkflowID") REFERENCES "applications"("ApplicationID")
        );
    """)

    conn.execute("""
        CREATE TABLE "workflow_events" (
            "Action"	TEXT,
            "resource"	TEXT,
            "Activity"	TEXT,
            "EventID"	TEXT,
            "OfferID"	TEXT,
            "startTime"	TEXT,
            "completeTime"	TEXT,
            "WorkflowID"	TEXT,
            PRIMARY KEY("EventID"),
            FOREIGN KEY("resource") REFERENCES "resources"("resource"),
            FOREIGN KEY("WorkflowID") REFERENCES "workflows"("WorkflowID")
        );
    """)
