import logging
from rag.retriever import retriever
from chatbot.llms.factory import get_llm

logger = logging.getLogger(__name__)

class RAGService:

    @staticmethod
    def generate_response(session, message):
        import time
        timing = {}
        session.timing = timing
        
        intent = session.current_intent

        try:
            # Step 1: Intent-filtered retrieval
            try:
                t0 = time.perf_counter()
                
                # Retrieval level determination happens inside search() initially, but it's very fast dict lookup.
                # Let's time search()
                
                state = session.entities.get("states")
                card_type = session.entities.get("card_types")
                
                timing["retrieval_level"] = (time.perf_counter() - t0) * 1000 # Approximation before passing to retriever

                t1 = time.perf_counter()
                result = retriever.search(
                    query=message,
                    top_k=5,
                    intent=intent,
                    state=state,
                    card_type=card_type
                )
                timing["chromadb"] = (time.perf_counter() - t1) * 1000
                print(f"[DEBUG RAG] Retriever = SUCCESS (Level: {result.get('retrieval_level')})")
            except Exception as e:
                import traceback
                print("[ERROR RAG] Retriever = FAILED")
                print(f"[ERROR RAG] Exception type: {type(e)}")
                print(f"[ERROR RAG] Traceback:\n{traceback.format_exc()}")
                return "I apologize, but I encountered a RETRIEVER_ERROR."
                
            # Step 2: Context construction
            try:
                t0 = time.perf_counter()
                documents = result.get("documents", [[]])[0]
                metadatas = result.get("metadatas", [[]])[0]
                distances = result.get("distances", [[]])[0]
                
                context_parts = []
                for doc, meta in zip(documents, metadatas):
                    title = meta.get("title", "Unknown")
                    category = meta.get("category", "Unknown")
                    context_parts.append(f"Title: {title}\nCategory: {category}\nContent: {doc}")
                
                context = "\n\n---\n\n".join(context_parts)
                timing["context"] = (time.perf_counter() - t0) * 1000
                print("[DEBUG RAG] Context = SUCCESS")
            except Exception as e:
                import traceback
                print("[ERROR RAG] Context = FAILED")
                print(f"[ERROR RAG] Traceback:\n{traceback.format_exc()}")
                return "I apologize, but I encountered a CONTEXT_ERROR."
            
            # Logging for observability
            print(f"[DEBUG RAG] Query: {message}")
            print(f"[DEBUG RAG] Intent: {intent}")
            print(f"[DEBUG RAG] Entities: {session.entities}")
            print(f"[DEBUG RAG] Retrieved Intent(s): {[m.get('intent') for m in metadatas]}")
            print(f"[DEBUG RAG] Distances: {distances}")
            print(f"[DEBUG INFO] Level: {result.get('retrieval_level')}, Retrieved Docs: {len(documents)}, Context Size: {len(context)} chars")
            
            # Cache Lookup
            try:
                from chatbot.services.cache_service import cache_service
                doc_ids = []
                if "ids" in result and result["ids"]:
                    doc_ids = result["ids"][0]
                
                cached_response = cache_service.get(
                    intent=intent,
                    entities=session.entities,
                    retrieval_level=result.get("retrieval_level", "none"),
                    doc_ids=doc_ids,
                    context=context,
                    history=session.history
                )
                if cached_response:
                    timing["gemini"] = 0
                    timing["response_construct"] = 0
                    print(f"[PHASE9_METRICS] {{\"entity_ext_ms\": {timing.get('entity_extraction', 0):.2f}, \"retrieval_ms\": {timing.get('chromadb', 0):.2f}, \"context_size\": {len(context)}, \"prompt_chars\": {len(context)}, \"gemini_ms\": 0.0, \"429\": false}}")
                    return cached_response
            except Exception as e:
                print(f"[ERROR RAG] Cache lookup failed: {e}")

            # Step 3: LLM Prompt
            try:
                llm = get_llm()
                
                t0 = time.perf_counter()
                prompt = f"""You are a helpful and knowledgeable Public Distribution System (PDS) AI Assistant.
Your task is to answer the user's question using ONLY the provided retrieved context.

INSTRUCTIONS:
- Answer using ONLY the retrieved context. Do not hallucinate or invent government procedures, rules, URLs, deadlines, or fees.
- If the available information in the context is insufficient to answer the query, explicitly state that the information is unavailable.
- Respect the user's detected intent and provided entities (e.g., state, district).
- Preserve state-specific information from the context if it applies to the user's entities.
- Do NOT expose internal routing, debug info, vector databases, ChromaDB, or retrieval scores.
- Present the final answer naturally to the user.

USER QUERY: {message}

DETECTED INTENT: {intent}
EXTRACTED ENTITIES: {session.entities}

RETRIEVED CONTEXT:
{context if context else "No context found."}
"""
                print(f"[DEBUG INFO] LLM Model being used: {getattr(llm, 'model_name', 'unknown')}")
                
                t_llm_start = time.perf_counter()
                response = llm.generate_response(prompt)
                t_llm_end = time.perf_counter()
                
                timing["gemini"] = (t_llm_end - t_llm_start) * 1000
                timing["response_construct"] = (time.perf_counter() - t_llm_end) * 1000
                
                print("[DEBUG RAG] LLM = SUCCESS")
                print(f"[PHASE9_METRICS] {{\"entity_ext_ms\": {timing.get('entity_extraction', 0):.2f}, \"retrieval_ms\": {timing.get('chromadb', 0):.2f}, \"context_size\": {len(context)}, \"prompt_chars\": {len(prompt)}, \"gemini_ms\": {timing['gemini']:.2f}, \"429\": false}}")
                
                try:
                    cache_service.set(
                        intent=intent,
                        entities=session.entities,
                        retrieval_level=result.get("retrieval_level", "none"),
                        doc_ids=doc_ids,
                        context=context,
                        history=session.history,
                        response=response
                    )
                except Exception as cache_e:
                    print(f"[ERROR RAG] Cache store failed: {cache_e}")
                
                return response
            except Exception as e:
                t_llm_end = time.perf_counter()
                timing["gemini"] = (t_llm_end - t_llm_start) * 1000
                import traceback
                with open("rag_crash.txt", "w") as f:
                    f.write(f"Exception: {str(e)}\n")
                    f.write(traceback.format_exc())
                print("[ERROR RAG] LLM = FAILED")
                print(f"[ERROR RAG] Exception message: {str(e)}")
                print("[ERROR RAG] Traceback:")
                traceback.print_exc()
                
                is_429 = "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)
                print(f"[DEBUG INFO] Encountered 429: {is_429}")
                print(f"[PHASE9_METRICS] {{\"entity_ext_ms\": {timing.get('entity_extraction', 0):.2f}, \"retrieval_ms\": {timing.get('chromadb', 0):.2f}, \"context_size\": {len(context)}, \"prompt_chars\": {len(prompt)}, \"gemini_ms\": {timing['gemini']:.2f}, \"429\": {str(is_429).lower()}}}")
                
                if is_429:
                    return "Our system is currently experiencing high traffic. Please try again in a few moments."
                return "I apologize, but our AI service is currently experiencing technical difficulties. Please check the official PDS portal."
            
        except Exception as e:
            return "I apologize, but I encountered an unexpected error. Please try again later."
