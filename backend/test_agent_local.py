import asyncio
from app.agents.base_agent import run_agent

def test_queries():
    queries = [
        "Find the daily report from last week",
        "Search for PDFs",
        "Find files containing the word 'marketing'",
        "Show me all images"
    ]
    for q in queries:
        print(f"Query: {q}")
        res = run_agent(q)
        print(f"Result: {res}\n")

if __name__ == "__main__":
    test_queries()
