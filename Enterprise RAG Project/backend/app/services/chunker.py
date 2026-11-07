from typing import List, Dict, Any

class ChunkingService:
    @staticmethod
    def recursive_character_chunking(
        text: str, chunk_size: int = 500, chunk_overlap: int = 50
    ) -> List[Dict[str, Any]]:
        """Splits text into chunks of specified size with overlap using recursive separator logic."""
        if not text:
            return []
        
        separators = ["\n\n", "\n", " ", ""]
        final_chunks = []
        
        def split_text(text_to_split: str) -> List[str]:
            for sep in separators:
                if sep == "":
                    return [text_to_split[i:i + chunk_size] for i in range(0, len(text_to_split), chunk_size - chunk_overlap)]
                if sep in text_to_split:
                    splits = text_to_split.split(sep)
                    merged = []
                    current = ""
                    for s in splits:
                        piece = s + sep if sep != " " else s + " "
                        if len(current) + len(piece) <= chunk_size:
                            current += piece
                        else:
                            if current:
                                merged.append(current.strip())
                            current = piece
                    if current:
                        merged.append(current.strip())
                    return merged
            return [text_to_split]

        raw_chunks = split_text(text)
        
        for idx, chunk in enumerate(raw_chunks):
            if chunk.strip():
                final_chunks.append({
                    "chunk_index": idx,
                    "content": chunk.strip(),
                    "char_count": len(chunk.strip())
                })
        
        return final_chunks
