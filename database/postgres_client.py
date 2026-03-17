# database/postgres_client.py

import psycopg2
from psycopg2 import sql
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PostgreSQLClient:
    """PostgreSQL client wrapper for database operations"""
    
    def __init__(self, config: Dict[str, Any], database: str):
        """
        Initialize PostgreSQL client
        
        Args:
            config: PostgreSQL connection configuration
            database: Database name to connect to
        """
        self.config = config.copy()
        self.config['database'] = database
        self.conn: Optional[psycopg2.extensions.connection] = None
        self.cursor: Optional[psycopg2.extensions.cursor] = None
    
    def initialize(self):
        """Initialize database connection"""
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to PostgreSQL database: {self.config['database']}")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logger.info(f"PostgreSQL connection closed for database: {self.config['database']}")
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as list of dictionaries
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dictionaries with column names as keys
        """
        try:
            self.cursor.execute(query, params)
            
            # Get column names
            columns = [desc[0] for desc in self.cursor.description]
            
            # Fetch all rows and convert to dictionaries
            rows = self.cursor.fetchall()
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))
            
            return results
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            self.conn.rollback()
            raise
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            logger.error(f"Error executing update: {e}")
            logger.error(f"Query: {query}")
            self.conn.rollback()
            raise
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Execute a query multiple times with different parameters
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Number of affected rows
        """
        try:
            self.cursor.executemany(query, params_list)
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            logger.error(f"Error executing batch query: {e}")
            logger.error(f"Query: {query}")
            self.conn.rollback()
            raise
    
    def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a query and return a single row
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Dictionary with column names as keys, or None if no results
        """
        try:
            self.cursor.execute(query, params)
            row = self.cursor.fetchone()
            
            if row is None:
                return None
            
            # Get column names
            columns = [desc[0] for desc in self.cursor.description]
            
            return dict(zip(columns, row))
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            self.conn.rollback()
            raise
