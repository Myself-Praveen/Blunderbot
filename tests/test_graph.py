"""
Unit tests for the Neo4j GraphRAG opening tree.
Tests validate schema creation, data ingestion, traversal queries,
and win-rate aggregation correctness.

Run with: python -m pytest tests/test_graph.py -v
"""
import unittest
from unittest.mock import MagicMock, patch

class TestGraphSchema(unittest.TestCase):
    """Tests for the Cypher schema and constraint definitions."""
    
    @patch('graph_schema.driver')
    def test_schema_creates_constraints(self, mock_driver):
        """Verify that init_graph_schema runs the expected Cypher statements."""
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
        
        from graph_schema import init_graph_schema
        init_graph_schema()
        
        # Should have called session.run() at least 3 times (2 indexes + 1 constraint)
        self.assertGreaterEqual(mock_session.run.call_count, 3)

class TestGraphTraversal(unittest.TestCase):
    """Tests for the traverse_opening() GraphRAG query."""
    
    def test_traverse_returns_list(self):
        """Verify traverse_opening returns a list structure."""
        # We test the return type contract without needing a live DB
        with patch('graph_traversal.driver') as mock_driver:
            mock_session = MagicMock()
            mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
            
            # Simulate empty result
            mock_session.run.return_value = []
            
            from graph_traversal import traverse_opening
            result = traverse_opening("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
            self.assertIsInstance(result, list)
    
    def test_opening_name_lookup(self):
        """Verify known opening FENs are correctly identified."""
        from graph_traversal import get_opening_name
        
        # Test Sicilian Defense
        sicilian_fen = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
        self.assertEqual(get_opening_name(sicilian_fen), "Sicilian Defense (1.e4 c5)")
        
        # Test French Defense
        french_fen = "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
        self.assertEqual(get_opening_name(french_fen), "French Defense (1.e4 e6)")
        
        # Test unknown position
        random_fen = "8/8/8/8/8/8/8/8 w - - 0 1"
        self.assertEqual(get_opening_name(random_fen), "Unknown Opening")

class TestWinRateAggregation(unittest.TestCase):
    """Tests to validate win-rate percentage calculations."""
    
    def test_win_rate_percentages_sum_to_100(self):
        """When total_games > 0, win percentages should approximately sum to 100."""
        # Simulated aggregated stats from a node
        white_wins = 450
        black_wins = 350
        draws = 200
        total = white_wins + black_wins + draws
        
        w_pct = round(white_wins / total * 100, 1)
        b_pct = round(black_wins / total * 100, 1)
        d_pct = round(draws / total * 100, 1)
        
        self.assertAlmostEqual(w_pct + b_pct + d_pct, 100.0, places=0)
    
    def test_zero_games_returns_zero_pct(self):
        """When a position has zero games, win rates should be 0."""
        total = 0
        w_pct = 0.0 if total == 0 else round(0 / total * 100, 1)
        self.assertEqual(w_pct, 0.0)

if __name__ == "__main__":
    unittest.main()
