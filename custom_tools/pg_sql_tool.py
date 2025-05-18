from pg import DB


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

    def find_tables(self) -> list[str]:
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

    # destroy class
    def __del__(self):
        """Destroy the PgSQLTool instance and close the connection pool."""
        if hasattr(self, "db"):
            self.db.close()
            print("Connection pool closed.")
        else:
            print("No connection pool to close.")
        # del self.db
