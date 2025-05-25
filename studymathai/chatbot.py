import os
import json
from openai import OpenAI
from typing import Optional, List, Dict
from studymathai.retriever import SlideRetriever
from studymathai.logging_config import get_logger

logger = get_logger(__name__)

class ChatContextManager:
    def __init__(self, history_file="chat_history.json"):
        self.history_file = history_file
        self._history = self.load()

    @property
    def history(self):
        return self._history

    def load(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load chat history: {e}")
        return []

    def append(self, message):
        self._history.append(message)

    def save(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self._history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save chat history: {e}")

class ContextAwareChatBot:
    def __init__(self, 
                 retriever: SlideRetriever,
                 context_manager: ChatContextManager,
                 tools: Optional[List[Dict]] = None):
        self.model = os.getenv("MODEL_NAME")
        self.client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
        self.retriever = retriever

        self.context_manager = context_manager
        self.history = self.context_manager.history
        self.tools = tools or self.default_tools()

    @staticmethod
    def default_tools():
        return [
            {
                "type": "function",
                "name": "query_knowledge_base",
                "description": "Search for relevant textbook notes using a vector database.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "keywords": {"type": "array", "items": {"type": "string"}},
                        "top_k": {"type": "integer", "default": 3}
                    },
                    "required": ["query", "keywords", "top_k"],
                    "additionalProperties": False
                }
            }
        ]

    def get_response(self, user_input: str, return_context=False) -> str:
        self.context_manager.append({"role": "user", "content": user_input})
        print("\n🧠 [INFO] Sending message to model...")

        response = self.client.responses.create(
            model=self.model,
            input=self.history,
            tools=self.tools,
            instructions="You are a helpful math tutor with access to a knowledge base of textbook slides.",
        )

        if response.output and response.output[0].type == "function_call":
            tool_call = response.output[0]
            print(f"🔧 [TOOL CALL] Model requested tool: {tool_call.name}")
            print(f"📦 Arguments: {tool_call.arguments}")
            
            self.context_manager.append(tool_call.model_dump())

            args = json.loads(tool_call.arguments)
            contexts = self.retriever.query(question=args["query"], top_k=args.get("top_k", 3))

            decks_list = []
            for context in contexts:
                deck = self.retriever.get_slide_deck(context["content_id"])
                if deck:
                    decks_list.append({
                        "segment_id": context["content_id"],
                        "heading": deck['heading'],
                        "slides": deck["slides"]
                    })

            self.context_manager.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": str(decks_list)
            })

            print("📤 [INFO] Tool executed and output added to history. Requesting final answer...\n")

            final_response = self.client.responses.create(
                model=self.model,
                input=self.history,
                tools=self.tools
            )
            
            self.context_manager.append({"role": "assistant", "content": final_response.output_text})
            self.context_manager.save()
            return (final_response.output_text, decks_list) if return_context else final_response.output_text

        else:
            print("💬 [INFO] Model responded directly without using a tool.")
            self.context_manager.append({"role": "assistant", "content": response.output_text})
            self.context_manager.save()
            return (response.output_text, []) if return_context else response.output_text
