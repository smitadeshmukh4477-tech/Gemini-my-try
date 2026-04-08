import json
import os
import random
import time
import re
from datetime import datetime
from duckduckgo_search import DDGS

MEMORY_FILE = "gemini_universal_soul.json"

class GeminiUltra:
    def __init__(self):
        self.memory = self.load_memory()
        self.active_topic = "General"
        # Internal Knowledge Base
        self.wiki = {
            "blox fruits": "Blox Fruits: Mirage Island spawns at night in Third Sea. Blue Gear is a glowing cog needed for Race V4.",
            "minecraft": "Technical MC: 1.21.1 is stable for Litematica. Redstone cannons need precise tick-delays for orbital strikes.",
            "8th grade": "NCERT 8th: Science (Cells, Microbes), Math (Rational Numbers, Squares). Focus on the fundamentals.",
            "cricket": "MS Dhoni (Thala): 2011 WC Winner. Jersey #7. The ultimate finisher."
        }

    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {"user_name": None, "history": [], "stats": {"chats": 0}}

    def save_memory(self):
        self.memory["history"] = self.memory["history"][-20:]
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=4, ensure_ascii=False)

    def web_search(self, query):
        """Ultra-Stable Search Core v6.9"""
        print(f"🌐 Scanning Satellites for: {query}...", end="\r")
        try:
            with DDGS() as ddgs:
                # Region 'wt-wt' and timelimit 'y' (last year) for fresh news
                results = ddgs.text(query, region='wt-wt', safesearch='moderate', timelimit='y')
                
                clean_results = []
                count = 0
                for r in results:
                    if count >= 3: break
                    # Filter out the 'Sign-in' and 'Google Search' junk
                    title = r['title'].lower()
                    body = r['body'].lower()
                    if "google" not in title and "sign in" not in body and "advanced search" not in title:
                        clean_results.append(f"📍 {r['title']}\n   {r['body']}\n")
                        count += 1
                
                if clean_results:
                    return f"\n--- LIVE DATA FETCH ---\n" + "".join(clean_results) + "-------------------"
                else:
                    return "No clean data found. Try: 'search [Topic] Wiki' for better results."
                    
        except Exception as e:
            return f"Search Error: {e}. (Try running 'pip install -U duckduckgo-search' in CMD)"

    def get_response(self, user_input: str) -> str:
        name = self.memory["user_name"] or "Guest"
        ui = user_input.lower().strip()
        self.memory["history"].append(ui)
        
        # --- 1. SYSTEM TASKS (Math) ---
        if any(op in ui for op in ["+", "-", "*", "/", "calculate"]):
            clean_expr = re.sub(r'[^0-9+\-*/().\s]', '', ui)
            try:
                return f"Math Engine: {clean_expr} = **{eval(clean_expr)}** 🔥"
            except: pass

        # --- 2. WEATHER CORE ---
        if "weather" in ui:
            city = ui.replace("weather", "").strip() or "Mumbai"
            return self.web_search(f"current weather temperature in {city}")

        # --- 3. SEARCH TASKS (Web Access) ---
        if ui.startswith("search "):
            query = ui.replace("search ", "").strip()
            return self.web_search(query)

        # --- 4. WIKI TASKS (Internal Knowledge) ---
        for key
        
