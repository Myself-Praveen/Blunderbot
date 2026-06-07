import os
from neo4j import GraphDatabase

# Neo4j Connection Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "blunderbot_dev")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def verify_connection():
    """
    Verifies Neo4j connectivity and prints the server version.
    Used as a health check on startup.
    """
    with driver.session() as session:
        result = session.run("RETURN 1 AS test")
        record = result.single()
        if record and record["test"] == 1:
            print("Neo4j connection established successfully.")
            return True
    return False

def close_driver():
    """Cleanly shuts down the Neo4j driver connection pool."""
    driver.close()

if __name__ == "__main__":
    if verify_connection():
        print("Health check passed.")
    else:
        print("Failed to connect to Neo4j.")
    close_driver()
