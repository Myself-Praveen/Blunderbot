from graph_db import driver

def init_graph_schema():
    """
    Defines the Cypher schema for our Opening Tree:
    
    (:Position {fen: String, move_number: Int})
        -[:MOVE {san: String, uci: String}]->
    (:Position {fen: String, move_number: Int})
    
    Each Position node stores the board FEN and aggregated statistics.
    Each MOVE relationship stores the SAN notation and UCI encoding.
    
    We also create indexes on FEN strings for O(1) lookup performance.
    """
    with driver.session() as session:
        # Create uniqueness constraint on FEN for deduplication
        session.run("""
            CREATE CONSTRAINT position_fen_unique IF NOT EXISTS
            FOR (p:Position) REQUIRE p.fen IS UNIQUE
        """)
        
        # Create index on move_number for efficient range queries (moves < 15)
        session.run("""
            CREATE INDEX position_move_number IF NOT EXISTS
            FOR (p:Position) ON (p.move_number)
        """)
        
        # Create index for win-rate aggregation queries
        session.run("""
            CREATE INDEX position_stats IF NOT EXISTS
            FOR (p:Position) ON (p.white_wins, p.black_wins, p.draws)
        """)
        
        print("Graph schema initialized with constraints and indexes.")

if __name__ == "__main__":
    init_graph_schema()
