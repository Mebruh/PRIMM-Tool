"""
SQL Query Validator
Provides validation and security checks for user-submitted SQL queries.
"""

import re
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where
from sqlparse.tokens import Keyword, DML


class SQLValidator:
    """Validates SQL queries for security and correctness."""
    
    # Dangerous SQL keywords that should be blocked
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 
        'CREATE', 'TRUNCATE', 'REPLACE', 'GRANT', 'REVOKE'
    ]
    
    def __init__(self, query):
        """
        Initialize validator with a SQL query.
        
        Args:
            query (str): The SQL query to validate
        """
        self.query = query.strip() if query else ""
        self.errors = []
    
    def validate(self):
        """
        Run all validation checks.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not self._check_not_empty():
            return False, "❌ Query is empty. Please enter a valid SQL query."
        
        if not self._check_no_dangerous_keywords():
            return False, "❌ Unsafe query detected. Only SELECT statements are allowed. As you cannot modify the database."
        
        if not self._check_valid_sql_syntax():
            return False, "❌ Invalid SQL syntax. Please check your query."
        
        return True, None
    
    def _check_not_empty(self):
        """Check if query is not empty."""
        return bool(self.query)
    
    def _check_no_dangerous_keywords(self):
        """Check if query contains dangerous SQL keywords."""
        query_upper = self.query.upper()
        return not any(keyword in query_upper for keyword in self.DANGEROUS_KEYWORDS)
    
    def _check_valid_sql_syntax(self):
        """
        Check if query has valid SQL syntax using sqlparse.
        
        Returns:
            bool: True if syntax appears valid
        """
        try:
            parsed = sqlparse.parse(self.query)
            if not parsed:
                return False
            
            # Check if it's a SELECT statement
            statement = parsed[0]
            if statement.get_type() != 'SELECT':
                return False
            
            return True
        except Exception:
            return False
    
    def normalize_table_names(self, table_mapping):
        """
        Replace user-friendly table names with actual Django table names.
        
        Args:
            table_mapping (dict): Dictionary mapping user table names to Django table names
                                 e.g., {'employees': 'website_employee'}
        
        Returns:
            str: Query with normalized table names
        """
        normalized_query = self.query
        for user_table, django_table in table_mapping.items():
            # Use word boundaries to avoid partial replacements
            pattern = r'\b' + re.escape(user_table) + r'\b'
            normalized_query = re.sub(pattern, django_table, normalized_query, flags=re.IGNORECASE)
        
        return normalized_query


class QueryComparator:
    """Compares user query results with expected results."""
    
    @staticmethod
    def normalize_data(data, rename_fields=None):
        """
        Normalize data for comparison by converting to lowercase and sorting.
        
        Args:
            data (list): List of dictionaries containing query results
            rename_fields (dict): Optional dictionary for renaming fields
        
        Returns:
            list: Normalized and sorted data
        """
        normalized = []
        for record in data:
            new_record = {k: str(v).strip().lower() for k, v in record.items()}
            
            # Rename fields if mapping provided
            if rename_fields:
                for old_name, new_name in rename_fields.items():
                    if old_name in new_record:
                        new_record[new_name] = new_record.pop(old_name)
            
            normalized.append(new_record)
        
        return sorted(normalized, key=lambda x: tuple(x.values()))
    
    @staticmethod
    def compare_results(user_result, expected_result, rename_fields=None):
        """
        Compare user query results with expected results.
        
        Args:
            user_result (list): Results from user's query
            expected_result (list): Expected results
            rename_fields (dict): Optional field name mapping
        
        Returns:
            bool: True if results match
        """
        normalized_user = QueryComparator.normalize_data(user_result, rename_fields)
        normalized_expected = QueryComparator.normalize_data(expected_result, rename_fields)
        
        return normalized_user == normalized_expected
    
    @staticmethod
    def compare_queries(user_query, expected_query):
        """
        Compare two SQL queries by normalizing whitespace and case.
        
        """
        def normalize_query(query):
            normalized = re.sub(r'\s+', '', query.lower())
            normalized = normalized.rstrip(';')
            return normalized
        
        return normalize_query(user_query) == normalize_query(expected_query)


class QueryHintGenerator:
    """Generates helpful hints when user queries are incorrect."""
    
    @staticmethod
    def generate_hint(user_query, expected_keywords):
        """
        Generate a hint based on what's missing from the user's query.
        
        Args:
            user_query (str): User's SQL query
            expected_keywords (dict): Dictionary of expected keywords and their hints
                                     e.g., {'salary': 'Check the column you are filtering by'}
        
        Returns:
            str: Helpful hint message
        """
        query_lower = user_query.lower()
        
        for keyword, hint in expected_keywords.items():
            if keyword.lower() not in query_lower:
                return hint
        
        return "Check your query syntax and conditions."
