"""
Main entry point for Architecture AI
"""

import argparse
from bot.engine import ArchitectureBot  # adjust import path to your project

def run():
    parser = argparse.ArgumentParser(description="Run Architecture AI bot")
    parser.add_argument("query", nargs="*", help="Input query for the bot")
    args = parser.parse_args()

    bot = ArchitectureBot()

    if args.query:
        query = " ".join(args.query)
        response = bot.run(query)
        print(response)
    else:
        print("No query provided. Example usage:")
        print("python main.py 'Check compliance for building plan A'")

if __name__ == "__main__":
    run()
