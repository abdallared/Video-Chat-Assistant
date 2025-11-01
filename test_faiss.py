import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
import numpy as np

def normalize(vectors):
    if isinstance(vectors, list):
        return [v / np.linalg.norm(v) if np.linalg.norm(v) != 0 else v for v in vectors]
    else:
        norm = np.linalg.norm(vectors)
        return vectors / norm if norm != 0 else vectors

# Test loading FAISS
print("Testing FAISS database...")

try:
    embedding = OllamaEmbeddings(model="nomic-embed-text")
    print("✅ Embedding model loaded")
    
    if os.path.exists("./faiss_index"):
        vectordb = FAISS.load_local("./faiss_index", 
                                  embedding,
                                  allow_dangerous_deserialization=True)
        print("✅ FAISS database loaded")
        
        # Test query
        test_question = "ما هي المناعة في النبات"
        print(f"\nTesting query: {test_question}")
        
        query_embedding = embedding.embed_query(test_question)
        normalized_query = normalize([query_embedding])[0]
        
        docs_and_scores = vectordb.similarity_search_with_score_by_vector(normalized_query, k=3)
        
        print(f"Found {len(docs_and_scores)} results:")
        for i, (doc, score) in enumerate(docs_and_scores):
            print(f"{i+1}. Score: {score:.4f}")
            print(f"   Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"   Text: {doc.page_content[:100]}...")
            print()
            
    else:
        print("❌ FAISS index not found")
        
except Exception as e:
    print(f"❌ Error: {e}")
