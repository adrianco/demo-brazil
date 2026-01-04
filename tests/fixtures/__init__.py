"""
Brazilian Soccer MCP Knowledge Graph - Test Fixtures Module

This module provides test data loading utilities for integration tests.
"""

from tests.fixtures.test_data_loader import DataLoader, load_test_data

# Alias for backwards compatibility
TestDataLoader = DataLoader

__all__ = ['DataLoader', 'TestDataLoader', 'load_test_data']
