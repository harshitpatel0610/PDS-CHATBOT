import time
import threading
import hashlib
import json

class SemanticCache:
    def __init__(self, ttl_seconds: int = 3600, max_entries: int = 1000):
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self.cache = {}
        self.lock = threading.Lock()

    def _cleanup(self):
        # Must be called with lock acquired
        now = time.time()
        keys_to_delete = [k for k, v in self.cache.items() if now - v['timestamp'] > self.ttl_seconds]
        for k in keys_to_delete:
            del self.cache[k]
            
        if len(self.cache) > self.max_entries:
            # simple LRU-ish: delete oldest
            sorted_items = sorted(self.cache.items(), key=lambda item: item[1]['timestamp'])
            excess = len(self.cache) - self.max_entries
            for i in range(excess):
                del self.cache[sorted_items[i][0]]

    def _generate_key(self, intent: str, entities: dict, retrieval_level: str, doc_ids: list, context: str, history: list) -> str:
        # Create a deterministic representation
        entities_str = json.dumps(entities, sort_keys=True)
        doc_ids_str = json.dumps(sorted(doc_ids)) if doc_ids else "[]"
        history_str = json.dumps(history, sort_keys=True) if history else "[]"
        
        raw_key = f"intent:{intent}|entities:{entities_str}|level:{retrieval_level}|docs:{doc_ids_str}|context:{context}|history:{history_str}"
        return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

    def get(self, intent: str, entities: dict, retrieval_level: str, doc_ids: list, context: str, history: list):
        key = self._generate_key(intent, entities, retrieval_level, doc_ids, context, history)
        
        with self.lock:
            self._cleanup()
            if key in self.cache:
                entry = self.cache[key]
                if time.time() - entry['timestamp'] <= self.ttl_seconds:
                    print(f"[CACHE HIT] Key: {key}")
                    return entry['response']
                else:
                    del self.cache[key]
            
        print(f"[CACHE MISS] Key: {key}")
        return None

    def set(self, intent: str, entities: dict, retrieval_level: str, doc_ids: list, context: str, history: list, response: str):
        # Do not cache error fallbacks
        if not response or response.strip() == "":
            return
            
        error_messages = [
            "Our system is currently experiencing high traffic",
            "encountered an LLM_ERROR",
            "encountered a RETRIEVER_ERROR",
            "encountered a CONTEXT_ERROR",
            "experiencing technical difficulties",
            "unexpected error"
        ]
        for err in error_messages:
            if err in response:
                return

        key = self._generate_key(intent, entities, retrieval_level, doc_ids, context, history)
        with self.lock:
            self.cache[key] = {
                'response': response,
                'timestamp': time.time()
            }
            self._cleanup()
        print(f"[CACHE STORE] Key: {key}")

cache_service = SemanticCache(ttl_seconds=3600, max_entries=1000)
