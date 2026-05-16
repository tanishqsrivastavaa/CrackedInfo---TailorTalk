from app.agents.agent import llm
from app.agents.drive_search_tool import drive_search_tool
from app.services.search_engine import params_from_message, safe_search_drive
from langchain_core.messages import HumanMessage, SystemMessage

tools = {"drive_search_tool": drive_search_tool}

base_agent = llm.bind_tools([drive_search_tool])


def run_agent(user_input: str):
    system_prompt = (
        "You are a Google Drive search assistant. "
        "For any file search request, call drive_search_tool with structured fields. "
        "Map name intent to name/name_match (exact vs contains), content intent to full_text, "
        "file type intent to mime_type aliases, and date intent to modified_after/modified_before."
    )
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_input)]
    response = base_agent.invoke(messages)

    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool = tools[tool_name]
        tool_result = tool.invoke(tool_args)
    else:
        params = params_from_message(user_input)
        tool_result = safe_search_drive(params)

    assistant_answer = response.content if isinstance(response.content, str) else "Here are the search results."
    if tool_result.get("error"):
        assistant_answer = f"I could not complete the Drive search: {tool_result['error']}"
    elif tool_result.get("count", 0) == 0:
        assistant_answer = "I did not find matching files in the configured Drive folder."
    elif not assistant_answer:
        assistant_answer = f"I found {tool_result['count']} matching files."

    return {
        "message": user_input,
        "assistant_answer": assistant_answer,
        "query": tool_result.get("query"),
        "count": tool_result.get("count", 0),
        "files": tool_result.get("files", []),
        "error": tool_result.get("error"),
    }
