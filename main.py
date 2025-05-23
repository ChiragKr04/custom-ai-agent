from dotenv import load_dotenv
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, find_tables_tool_pgsql, find_table_column_name_and_datatype, run_sql_query
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()


class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]
    research_time: str


gemini = ChatOpenAI(
    model="gpt-4.1-nano",
)
# claude = ChatAnthropic()
# gemini = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
# )

chat_history = []

# open file from  this location prompts/gemini.txt and save its content to a variable
gemini_prompt = ""
# with open("./prompts/chatgpt_2025_03_24.txt", "r") as file:
#     gemini_prompt = file.read()

parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            {gemini_prompt}\n
            You are only allowed to give your response in the given format, you are not allowed to give reponse in plain text only use the format given below.
            {format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(
    format_instructions=parser.get_format_instructions(),
    gemini_prompt=gemini_prompt,
    chat_history=chat_history,
    agent_scratchpad="",
)

tools = [find_tables_tool_pgsql, find_table_column_name_and_datatype, run_sql_query]
agent = create_tool_calling_agent(
    llm=gemini,
    tools=tools,
    prompt=prompt,
)


def runGemini(prompt: str) -> dict[str, any]:
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
    )
    response = agent_executor.invoke(
        {
            "query": prompt,
            "chat_history": chat_history,
            "gemini_prompt": gemini_prompt,
            "format_instructions": parser.get_format_instructions(),
            "agent_scratchpad": "",
        }
    )
    return response


firstTime = True

while True:
    query = input(firstTime and "How can I help you?: " or "Tell me more: ")
    chat_history.append(HumanMessage(content=query))
    response = runGemini(query)
    try:
        structured_response = parser.parse(response.get("output"))
        chat_history.append(
            AIMessage(
                content=structured_response.summary,
                additional_kwargs={
                    "sources": structured_response.sources,
                    "tools_used": structured_response.tools_used,
                    "research_time": structured_response.research_time,
                },
            )
        )
        print(structured_response.summary)
        firstTime = False
    except Exception as e:
        print("Error parsing response:", e)
