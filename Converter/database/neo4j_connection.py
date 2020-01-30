import neo4j
from neobolt.exceptions import ServiceUnavailable
from log.logger import Logger

log = Logger.instance()


class Neo4JConnection:

    __driver = None
    __jdbc = None
    __user = None
    __pw = None

    def __init__(self, jdbc: str, user: str, pw: str):
        self.__jdbc = jdbc
        self.__user = user
        self.__pw = pw

    """ Returns a driver, connected to the Neo4J database instance specified in the constructor
    """
    def get_driver(self) -> neo4j.Driver:
        if (self.__driver is None) or (self.__driver.closed()):
            self.__driver = neo4j.GraphDatabase.driver(self.__jdbc, auth=(self.__user, self.__pw))

        return self.__driver

    """ Fires a query to Neo4J and returns its results
    """
    def query(self, q: str, message=None):
        driver = self.get_driver()
        message = message.rstrip()
        if message is not None:
            log.info(f'Executing query: {message}')

        log.debug(q)

        try:
            executed_query = driver.session().run(q)
            results = executed_query.values()
            return results
        except ServiceUnavailable:
            print("Session dropped while executing query, retrying")
            self.query(q)

    def close(self):
        self.get_driver().close()
