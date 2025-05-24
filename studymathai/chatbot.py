import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from studymathai.db import DatabaseManager
from studymathai.retriever import SlideRetriever

load_dotenv()

class ChatBot:
    def __init__(self, history_file="chat_history.json"):
        self.model = os.getenv("MODEL_NAME", "gpt-4o")
        self.client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
        self.history_file = history_file
        self.history = self.load_history()

        self.db = DatabaseManager()
        chroma_path = os.getenv("CHROMA_DIRECTORY", "./chroma_index")
        self.retriever = SlideRetriever(self.db, persist_dir=chroma_path)

        self.tools = [
            {
                "type": "function",
                "name": "query_knowledge_base",
                "description": "Search for relevant textbook notes using a vector database.",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "top_k": {
                            "type": "integer",
                            "default": 3
                        },
                    },
                    "required": ["query", "keywords", "top_k"],
                    "additionalProperties": False
                }
            }
        ]

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
        except Exception:
            pass

    def get_response(self, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})
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
            self.history.append(tool_call)

            args = json.loads(tool_call.arguments)
            contexts = self.retriever.query(question=args["query"], top_k=args.get("top_k", 3))

            results = []
            for context in contexts:
                content_id = context["content_id"]
                deck = self.retriever.get_slide_deck(content_id)
                results.append(deck)

            self.history.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": json.dumps(results, indent=2)
            })

            print("📤 [INFO] Tool executed and output added to history. Requesting final answer...\n")

            response = self.client.responses.create(
                model=self.model,
                input=self.history,
                tools=self.tools
            )

        else:
            print("💬 [INFO] Model responded directly without using a tool.")

        if response.output_text:
            self.history.append({"role": "assistant", "content": response.output_text})
            self.save_history()
            return response.output_text.strip()

        return "[No response from model]"
