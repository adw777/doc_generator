import getpass
import os
from langchain_groq import ChatGroq
from groq import Groq
from langgraph.prebuilt import create_react_agent
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper


for env_var in [
    "GITHUB_APP_ID",
    "GITHUB_APP_PRIVATE_KEY",
    "GITHUB_REPOSITORY",
]:
    if not os.getenv(env_var):
        os.environ[env_var] = getpass.getpass()

github = GitHubAPIWrapper()
toolkit = GitHubToolkit.from_github_api_wrapper(github)

os.environ["GROQ_API_KEY"] = getpass.getpass()

from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant")


tools = [tool for tool in toolkit.get_tools() if tool.name == "Overview of existing files in Main branch"]
assert len(tools) == 1
tools[0].name = "Overview of existing files in Main branch"

example_query = "What is the installation process for this repo?"

events = agent_executor.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()

