from app.core.config import settings
from langchain_groq import ChatGroq
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage

if settings.GROQ_API_KEY:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", api_key=settings.GROQ_API_KEY, temperature=0.2
    )
else:
    llm = FakeMessagesListChatModel(responses=[AIMessage(content="")])
