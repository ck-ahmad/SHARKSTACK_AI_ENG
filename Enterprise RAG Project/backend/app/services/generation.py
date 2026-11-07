from typing import List, Dict, Any, Generator
import json

class PromptPipelineService:
    @staticmethod
    def build_rag_prompt(query: str, retrieved_context: List[Dict[str, Any]]) -> str:
        context_str = ""
        for idx, item in enumerate(retrieved_context, 1):
            context_str += f"\n[Source {idx}] Chunk ID: {item.get('chunk_id')}\nContent: {item.get('content')}\n"

        prompt = f"""You are EnterpriseIQ, an intelligent enterprise assistant. Answer the question using ONLY the provided context below.
Always cite your sources using [Source X] format.

Context Information:
{context_str}

User Question: {query}

Answer:"""
        return prompt

class CitationEngine:
    @staticmethod
    def format_sources(retrieved_context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sources = []
        for idx, item in enumerate(retrieved_context, 1):
            sources.append({
                "source_index": idx,
                "source_tag": f"[Source {idx}]",
                "chunk_id": item.get("chunk_id"),
                "content_preview": item.get("content", "")[:100] + "..." if len(item.get("content", "")) > 100 else item.get("content", ""),
                "score": item.get("rrf_score", item.get("score", 0.0))
            })
        return sources

class LLMGenerationEngine:
    @staticmethod
    def generate_response(prompt: str, retrieved_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not retrieved_context:
            return {
                "answer": "I could not find relevant information in the uploaded enterprise documents to answer your query.",
                "citations": []
            }
        
        # Synthesize answer with citations based on top retrieved chunks
        top_chunk = retrieved_context[0]["content"]
        citations = CitationEngine.format_sources(retrieved_context)
        
        answer = f"Based on the enterprise context [Source 1], {top_chunk}"
        if len(retrieved_context) > 1:
            answer += f" Additional details indicate that {retrieved_context[1]['content']} [Source 2]."
            
        return {
            "answer": answer,
            "citations": citations
        }
