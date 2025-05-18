from dotenv import load_dotenv
from pydantic import BaseModel

# from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, find_tables_tool_pgsql

load_dotenv()


class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]
    research_time: str


# chatGPT = ChatOpenAI()
# claude = ChatAnthropic()
gemini = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
)

# open file from  this location prompts/gemini.txt and save its content to a variable
gemini_prompt = ""
with open("./prompts/gemini.txt", "r") as file:
    gemini_prompt = file.read()

parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            {format_instructions}
            {gemini_prompt}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(
    format_instructions=parser.get_format_instructions(),
    gemini_prompt=gemini_prompt,
)

tools = [search_tool, find_tables_tool_pgsql]
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
    print(agent_executor.tools)
    response = agent_executor.invoke(
        {
            "query": prompt,
            # "chat_history": "",
            # "agent_scratchpad": "",
        }
    )
    return response


firstTime = True

while True:
    query = input(firstTime and "How can I help you?: " or "Tell me more: ")
    response = runGemini(query)
    # Print the response
    # print(response)
    try:
        structured_response = parser.parse(response.get("output"))
        print(structured_response.summary)
        firstTime = False
    except Exception as e:
        print("Error parsing response:", e)
