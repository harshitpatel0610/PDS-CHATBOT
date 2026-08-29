import sys
import time
import uuid
import json
import numpy as np

from chatbot.services.chat_service import chat_service
from rag.retriever import retriever
from rag.embeddings import embedding_service

def run_benchmark():
    metrics = []
    
    print("Starting Phase 9 Benchmark...")
    
    t_start = time.perf_counter()
    
    # Manually trigger startup
    retriever.initialize()
    
    startup_ms = (time.perf_counter() - t_start) * 1000
    print(f"Startup Time: {startup_ms:.2f} ms")
    
    # Initial warmup conversation
    print("\n--- Initial Warmup Request ---")
    warmup_sid = str(uuid.uuid4())
    chat_service.process_message(warmup_sid, "How can I apply for a new ration card?")
    chat_service.process_message(warmup_sid, "Gujarat")
    chat_service.process_message(warmup_sid, "Sabarkantha")
    chat_service.process_message(warmup_sid, "APL")
    
    print("Warmup complete. Delaying 65s to reset quota completely...")
    time.sleep(65)
    
    for i in range(1, 11):
        sid = str(uuid.uuid4())
        print(f"\n--- Request {i} (Session: {sid}) ---")
        
        chat_service.process_message(sid, "How can I apply for a new ration card?")
        chat_service.process_message(sid, "Gujarat")
        chat_service.process_message(sid, "Sabarkantha")
        
        # Final request
        import io
        from contextlib import redirect_stdout
        
        t_req_start = time.perf_counter()
        
        f = io.StringIO()
        with redirect_stdout(f):
            res = chat_service.process_message(sid, "APL")
            
        t_req_total = (time.perf_counter() - t_req_start) * 1000
        
        stdout_str = f.getvalue()
        sys.stdout.write(stdout_str) # print it out so we can see it
        
        # Parse metrics from stdout
        m = None
        for line in stdout_str.split('\n'):
            if line.startswith("[PHASE9_METRICS]"):
                m_str = line.replace("[PHASE9_METRICS] ", "").strip()
                try:
                    m = json.loads(m_str)
                except:
                    pass
        
        if m:
            m["total_ms"] = t_req_total
            m["retry"] = m["429"]
            metrics.append(m)
            print(f"Total: {t_req_total:.2f}ms | Gemini: {m['gemini_ms']:.2f}ms | Chroma: {m['retrieval_ms']:.2f}ms | 429: {m['429']}")
        else:
            print(f"Total: {t_req_total:.2f}ms | Metrics missing from stdout")
        
        time.sleep(15.0)

    print("\n\n=== PHASE 9 PERFORMANCE REPORT ===")
    print(f"Startup: {startup_ms:.2f} ms")
    
    if not metrics:
        print("No metrics collected.")
        return
        
    totals = [m["total_ms"] for m in metrics]
    geminis = [m["gemini_ms"] for m in metrics]
    chromas = [m["retrieval_ms"] for m in metrics]
    entitys = [m["entity_ext_ms"] for m in metrics]
    num_429s = sum(1 for m in metrics if m["429"])
    
    print("\nTotal Request:")
    print(f"Average: {np.mean(totals):.2f} ms")
    print(f"P50: {np.percentile(totals, 50):.2f} ms")
    print(f"P90: {np.percentile(totals, 90):.2f} ms")
    print(f"P95: {np.percentile(totals, 95):.2f} ms")
    print(f"Maximum: {np.max(totals):.2f} ms")
    print(f"Minimum: {np.min(totals):.2f} ms")
    
    print("\nGemini Request:")
    print(f"Average: {np.mean(geminis):.2f} ms")
    print(f"P50: {np.percentile(geminis, 50):.2f} ms")
    print(f"P90: {np.percentile(geminis, 90):.2f} ms")
    print(f"P95: {np.percentile(geminis, 95):.2f} ms")
    print(f"Maximum: {np.max(geminis):.2f} ms")
    print(f"Minimum: {np.min(geminis):.2f} ms")

    print("\nOther:")
    print(f"Avg Entity Extraction: {np.mean(entitys):.2f} ms")
    print(f"Avg ChromaDB Retrieval: {np.mean(chromas):.2f} ms")
    print(f"Avg Context Size: {np.mean([m['context_size'] for m in metrics]):.2f} chars")
    
    print(f"\n429 count: {num_429s}")
    print(f"Retry count: {num_429s}")  # google-genai retry implies 429
    
if __name__ == '__main__':
    run_benchmark()
