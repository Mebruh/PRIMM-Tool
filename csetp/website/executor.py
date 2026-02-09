"""
SQL Query Executor
Safely executes SQL queries against the database with proper error handling.
"""

from django.db import connection
from contextlib import contextmanager


class QueryExecutor:
    """Executes SQL queries safely with proper error handling."""
    
    @staticmethod
    @contextmanager
    def get_cursor():
        """
        Context manager for database cursor with automatic cleanup.
        
        Yields:
            cursor: Database cursor object
        """
        cursor = connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
    
    @staticmethod
    def execute_query(query):
        """
        Execute a SELECT query and return results.
        
        Args:
            query (str): SQL SELECT query to execute
        
        Returns:
            tuple: (success, data/error_message)
                  success (bool): True if execution succeeded
                  data (list): List of dictionaries with results if success
                  error_message (str): Error message if failure
        """
        try:
            with QueryExecutor.get_cursor() as cursor:
                cursor.execute(query)
                
                # Get column names from cursor description
                columns = [col[0] for col in cursor.description]
                
                # Fetch all rows and convert to list of dictionaries
                rows = cursor.fetchall()
                results = [dict(zip(columns, row)) for row in rows]
                
                return True, results
        
        except Exception as e:
            error_message = f"❌ SQL Execution Error: {str(e)}"
            return False, error_message
    
    @staticmethod
    def execute_query_single_value(query):
        """
        Execute a query that returns a single value (e.g., COUNT, SUM).
        
        Args:
            query (str): SQL query to execute
        
        Returns:
            tuple: (success, value/error_message)
        """
        try:
            with QueryExecutor.get_cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()[0]
                return True, result
        
        except Exception as e:
            error_message = f"❌ SQL Execution Error: {str(e)}"
            return False, error_message
    
    @staticmethod
    def test_query_syntax(query):
        """
        Test if a query has valid syntax without committing results.
        
        Args:
            query (str): SQL query to test
        
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            with QueryExecutor.get_cursor() as cursor:
                cursor.execute(query)
                # Don't fetch results, just check if it executes
            return True, None
        
        except Exception as e:
            return False, str(e)
