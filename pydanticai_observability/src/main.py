import logging
import os

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent

logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(verbose=True)


def main():
    agent = Agent(
        "google-gla:gemini-2.0-flash-lite",
        system_prompt="You are a helpful assistant that can search the web for information.",
        instrument=True,
    )
    history = []

    try:
        while True:
            query = input("Enter a query: ")
            if history:
                result = agent.run_sync(query, message_history=history[-1])
            else:
                result = agent.run_sync(query)
            logger.info(result.new_messages())
            history.append(result.new_messages())
            print(result.output)
    except KeyboardInterrupt:
        print("\nChat has been stopped by user.")


if __name__ == "__main__":
    main()
