import psycopg2
from psycopg2.extras import DictCursor
from typing import Any, Union


class PgSQLTool:
    """Tool for executing SQL queries on PostgreSQL databases."""

    def __init__(
        self, username: str, password: str, host: str, port: int, database: str
    ):
        """
        Initialize the PgSQLTool with connection parameters.

        Args:
            username (str): The username for the PostgreSQL database.
            password (str): The password for the PostgreSQL database.
            host (str): The host for the PostgreSQL database.
            port (int): The port for the PostgreSQL database.
            database (str): The database name for the PostgreSQL database.
        """
        self.connection_params = {
            "host": host,
            "port": int(port),
            "user": username,
            "password": password,
            "dbname": database,
        }
        
        try:
            print("Connecting to PostgreSQL database...")
            print(
                f"Connecting to database: {database} at {host}:{port} with user: {username}, password: {password}"
            )
            # Test connection
            conn = self._get_connection()
            conn.close()
            print(f"Successfully connected to database: {database}")
        except Exception as e:
            print(f"Failed to connect to database: {e}")
    
    def _get_connection(self):
        """Get a new database connection"""
        return psycopg2.connect(**self.connection_params)

    def find_tables(
        self,
        tool_input: Union[str, dict[str, Any]],
        **kwargs: Any,
    ) -> list[str]:
        """
        Retrieves a list of table names from the 'public' schema in the database.

        Returns:
            list[str]: A list of table names. Returns an empty list if an error occurs.
        """
        tables_list: list[str] = []
        conn = None

        try:
            # Get a connection
            conn = self._get_connection()
            cursor = conn.cursor()

            # Execute the SQL query to get table names
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
            cursor.execute(query)

            # Extract table names from the result
            tables_list = [row[0] for row in cursor.fetchall()]

            cursor.close()

        except Exception as e:
            print(f"Error: {e}")

        finally:
            if conn:
                # Close the connection
                conn.close()

        return tables_list
    
    def find_table_column_name_and_datatype(
        self,
        table_name: str,
    ) -> list[dict[str, Any]]:
        """
        Retrieves all the column names and its data type
        Args:
            table_name (str): The name of the table to retrieve the column names and data type from

        Returns:
            list[dict[str, Any]]: A list dictionary of all the names of column along with data type of column
        """
        column_data = []
        conn = None
        
        try:
            # Get a connection
            conn = self._get_connection()
            cursor = conn.cursor()

            # Execute the SQL query to get table names
            query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
            cursor.execute(query)
            result = cursor.fetchall()

            # Extract table names from the result
            column_data = [
                {
                    "columnName": row[0], 
                    "columnDataType": row[1]
                }
                for row in result
            ]

        except Exception as e:
            print(f"Error: {e}")

        finally:
            if conn:
                # Close the connection
                conn.close()
                conn = None

        return column_data
    
    def run_sql_query(
        self,
        query: str,
    ) -> list[dict[str, Any]]:
        """
        Runs a SQL query in a READ ONLY transaction on the PostgreSQL database.
        Args:
            query (str): The SQL query to run

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing the results of the query
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION READ ONLY")
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.execute("COMMIT")
            return result
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if conn:
                conn.close()
                conn = None

        return []
    
    # destroy class
    # def __del__(self):
    #     """Destroy the PgSQLTool instance and close the connection pool."""
    #     if hasattr(self, "db"):
    #         self.db.close()
    #         print("Connection pool closed.")
    #     else:
    #         print("No connection pool to close.")
    #     # del self.db
