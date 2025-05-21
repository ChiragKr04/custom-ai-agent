import os
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from custom_tools.pg_sql_tool import PgSQLTool

load_dotenv()

__search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    description="Useful for when you need to do a search on the internet to find information about a query.",
    func=__search.run,
)

__pgSQL = PgSQLTool(
    database=os.getenv("PGSQL_DATABASE"),
    host=os.getenv("PGSQL_HOST"),
    port=os.getenv("PGSQL_PORT"),
    username=os.getenv("PGSQL_USERNAME"),
    password=os.getenv("PGSQL_PASSWORD"),
)

find_tables_tool_pgsql = Tool(
    name="find_tables_inside_database_pgsql",
    description="Useful for when you need to find the schema and tables of your database",
    func=__pgSQL.find_tables,
)

find_table_column_name_and_datatype = Tool(
    name="find_table_column_name_and_datatype",
    description="Useful for when you need to find all the columns and column datatypes of a particular table inside postgresql db. You just need to pass table name as table_name=whatever_table_name is and it will return list[dict[str, Any]]",
    func=__pgSQL.find_table_column_name_and_datatype,
)
