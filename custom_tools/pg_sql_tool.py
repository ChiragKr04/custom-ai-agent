from pg import DB
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

        try:
            print("Connecting to PostgreSQL database...")
            print(
                f"Connecting to database: {database} at {host}:{port} with user: {username}, password: {password}"
            )
            self.db = DB(
                host=host,
                port=int(port),
                user=username,
                passwd=password,
                dbname=database,
            )
            print(f"Successfully connected to database: {database}")
        except Exception as e:
            print(f"Failed to connect to database: {e}")

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
            # Get a connection from the pool
            conn = self.db

            # Execute the SQL query to get table names
            query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
            result = conn.query(query)

            # Extract table names from the result
            tables_list = [row[0] for row in result]

        except Exception as e:
            print(f"Error: {e}")

        finally:
            if conn:
                # Close the connection
                conn.close()
                conn = None

        return tables_list
    
    async def find_table_column_name_and_datatype(
        self,
        table_name: str,
        tool_input: Union[str, dict[str, Any]],
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Retrieves all the column names and its data type

        Returns:
            list[dict[str, Any]]: A list dictionary of all the names of column along with data type of column
        """
        column_data = []
        conn = None
        print('TABLE NAME', table_name)
        print('TABLE NAME', tool_input)
        try:
            # Get a connection from the pool
            conn = self.db

            # Execute the SQL query to get table names
            query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
            result = await conn.query(query)

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


    # destroy class
    # def __del__(self):
    #     """Destroy the PgSQLTool instance and close the connection pool."""
    #     if hasattr(self, "db"):
    #         self.db.close()
    #         print("Connection pool closed.")
    #     else:
    #         print("No connection pool to close.")
    #     # del self.db
