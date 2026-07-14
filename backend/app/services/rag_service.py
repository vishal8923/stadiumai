import os
import json
import re
from typing import List, Dict, Any, Tuple

# Base directory for the data files
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

class RAGService:
    def __init__(self):
        self.files = {
            "faq": os.path.join(DATA_DIR, "faq.json"),
            "policies": os.path.join(DATA_DIR, "policies.json"),
            "food_menus": os.path.join(DATA_DIR, "food_menus.json"),
            "transport": os.path.join(DATA_DIR, "transport.json"),
            "emergency": os.path.join(DATA_DIR, "emergency.json"),
            "accessibility": os.path.join(DATA_DIR, "accessibility.json")
        }
        self.data_cache = {}
        self._load_all_data()

    def _load_all_data(self):
        """
        Loads all JSON datasets into memory.
        """
        for category, file_path in self.files.items():
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        self.data_cache[category] = json.load(f)
                except Exception as e:
                    self.data_cache[category] = []
            else:
                self.data_cache[category] = []

    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search RAG data files for the top matches.
        Score weights:
          - Match in keywords list: 3 points
          - Match in primary title/question/scenario/policy name: 2 points
          - Match in description/answer/content: 1 point
        """
        # Load data if cache empty (safeguard)
        if not self.data_cache:
            self._load_all_data()

        # Tokenize query
        query_words = [w.lower() for w in re.findall(r'\w+', query) if len(w) > 2]
        if not query_words:
            # Fallback to single words if all words are short
            query_words = [w.lower() for w in re.findall(r'\w+', query)]
            
        scored_results = []

        # Iterate over all categories
        for category, items in self.data_cache.items():
            for item in items:
                score = 0
                
                # 1. Keywords matching (weight = 3 per matching word)
                keywords = item.get("keywords", [])
                for kw in keywords:
                    if not kw:
                        continue
                    kw_lower = str(kw).lower()
                    for qw in query_words:
                        if qw == kw_lower or qw in kw_lower:
                            score += 3

                # 2. Title matching (weight = 2 per word overlap)
                # Primary text depends on category keys
                title_text = ""
                if "question" in item:
                    title_text = item["question"]
                elif "policy" in item:
                    title_text = item["policy"]
                elif "name" in item:
                    title_text = item["name"]
                elif "scenario" in item:
                    title_text = item["scenario"]
                elif "service_type" in item:
                    title_text = item["service_type"]
                elif "route" in item:
                    title_text = item["route"]

                title_lower = title_text.lower()
                for qw in query_words:
                    if qw in title_lower:
                        score += 2

                # 3. Body text matching (weight = 1 per word overlap)
                body_text = ""
                if "answer" in item:
                    body_text = item["answer"]
                elif "description" in item:
                    body_text = item["description"]
                elif "content" in item:
                    body_text = item["content"]
                elif "protocol" in item:
                    body_text = item["protocol"]
                elif "details" in item:
                    body_text = item["details"]
                elif "menu" in item:
                    # JSON serialized menu items
                    body_text = " ".join([m.get("item", "") for m in item.get("menu", [])])
                elif "schedule_details" in item:
                    body_text = item["schedule_details"]

                body_lower = body_text.lower()
                for qw in query_words:
                    if qw in body_lower:
                        score += 1

                if score > 0:
                    # Calculate confidence score (normalized between 0.0 and 1.0 roughly)
                    max_possible = len(query_words) * 6
                    confidence = min(1.0, score / max_possible) if max_possible > 0 else 0.1
                    
                    scored_results.append({
                        "category": category,
                        "item": item,
                        "score": score,
                        "confidence": round(confidence, 2)
                    })

        # Sort by score descending, then confidence descending
        scored_results.sort(key=lambda x: (-x["score"], -x["confidence"]))
        
        # Take top items and format
        results = []
        for r in scored_results[:limit]:
            results.append({
                "category": r["category"],
                "content": r["item"],
                "confidence_score": r["confidence"]
            })
            
        return results
