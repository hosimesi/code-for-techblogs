from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv(verbose=True)

agent = Agent("google-gla:gemini-2.0-flash-lite")

result_sync = agent.run_sync("What is the capital of Italy?")
print(result_sync.output)
# > Rome
