import streamlit as st
import time
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Try to import web search
try:
    from ddgs import DDGS
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False
    st.warning("Web search not available. Install ddgs package for web search functionality.")

# --- Page Configuration ---
st.set_page_config(
    page_title="🎥 Video Chat Assistant", 
    page_icon="🎥", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .video-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        height: 600px;
        overflow-y: auto;
    }
    
    .source-indicator {
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }
    
    .video-source {
        background-color: #d4edda;
        color: #155724;
    }
    
    .web-source {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    
    .simple-source {
        background-color: #fff3cd;
        color: #856404;
    }
    
    .sidebar-info {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Arabic text styling */
    .arabic-text, .stChatMessage {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Override for English content */
    .english-text {
        direction: ltr;
        text-align: left;
    }
    
    /* Chat message styling */
    .stChatMessage[data-testid="chat-message"] {
        direction: rtl;
        text-align: right;
    }
    
    /* Chat input styling */
    .stChatInput {
        direction: rtl;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False
if "transcriptions_loaded" not in st.session_state:
    st.session_state.transcriptions_loaded = False
if "transcriptions_data" not in st.session_state:
    st.session_state.transcriptions_data = []

@st.cache_data
def load_transcriptions():
    """Load transcription files"""
    transcriptions = []
    folder = r"./transcriptions"
    
    if not os.path.exists(folder):
        return []
    
    for fn in os.listdir(folder):
        if fn.endswith(".txt"):
            try:
                with open(os.path.join(folder, fn), 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        transcriptions.append({
                            "filename": fn,
                            "content": content,
                            "word_count": len(content.split())
                        })
            except Exception as e:
                st.error(f"Error loading {fn}: {e}")
                continue
    
    return transcriptions

def smart_text_search(question: str, transcriptions: list, top_k: int = 3):
    """Smart text search using TF-IDF similarity"""
    if not transcriptions:
        return []
    
    try:
        # Prepare documents
        documents = [t["content"] for t in transcriptions]
        documents.append(question)  # Add question as last document
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=None,  # Keep Arabic stop words
            ngram_range=(1, 2)  # Use unigrams and bigrams
        )
        
        # Fit and transform
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        # Calculate similarity between question and each document
        question_vector = tfidf_matrix[-1]  # Last document is the question
        doc_vectors = tfidf_matrix[:-1]     # All except question
        
        similarities = cosine_similarity(question_vector, doc_vectors).flatten()
        
        # Get top results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.05:  # Minimum similarity threshold
                results.append({
                    "text": transcriptions[idx]["content"],
                    "metadata": {"source": transcriptions[idx]["filename"]},
                    "score": float(similarities[idx]),
                    "word_count": transcriptions[idx]["word_count"]
                })
        
        return results
        
    except Exception as e:
        st.error(f"Error in smart text search: {e}")
        # Fallback to simple keyword search
        return simple_keyword_search(question, transcriptions, top_k)

def simple_keyword_search(question: str, transcriptions: list, top_k: int = 3):
    """Simple keyword-based search as fallback"""
    if not transcriptions:
        return []
    
    # Extract keywords from question
    question_words = set(re.findall(r'\b\w+\b', question.lower()))
    
    results = []
    for trans in transcriptions:
        content_words = set(re.findall(r'\b\w+\b', trans["content"].lower()))
        
        # Calculate word overlap
        overlap = len(question_words.intersection(content_words))
        score = overlap / len(question_words) if question_words else 0
        
        if score > 0.1:  # Minimum threshold
            results.append({
                "text": trans["content"],
                "metadata": {"source": trans["filename"]},
                "score": score,
                "word_count": trans["word_count"]
            })
    
    # Sort by score and return top results
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def search_web(question: str, max_results: int = 3):
    """Search web using DuckDuckGo"""
    if not WEB_SEARCH_AVAILABLE:
        return []
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(question, max_results=max_results))
        
        web_results = []
        for r in results:
            if r.get("body") and r.get("href"):
                web_results.append({
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "href": r.get("href", ""),
                    "snippet": r.get("body", "")[:300] + "..." if len(r.get("body", "")) > 300 else r.get("body", "")
                })
        
        return web_results
        
    except Exception as e:
        st.error(f"Web search error: {e}")
        return []

def generate_response(question: str, video_results: list, web_results: list = None):
    """Generate response based on search results"""
    response_parts = []
    
    if video_results:
        response_parts.append("بناءً على محتوى الفيديو:")
        
        for i, result in enumerate(video_results[:2], 1):
            response_parts.append(f"\n📄 **من الملف {result['metadata']['source']}**")
            
            # Extract relevant snippet
            text = result['text']
            if len(text) > 400:
                # Try to find relevant portion
                words = question.lower().split()
                best_snippet = text[:400]
                
                for word in words:
                    if word in text.lower():
                        pos = text.lower().find(word)
                        start = max(0, pos - 200)
                        end = min(len(text), pos + 200)
                        best_snippet = text[start:end]
                        if start > 0:
                            best_snippet = "..." + best_snippet
                        if end < len(text):
                            best_snippet = best_snippet + "..."
                        break
                
                response_parts.append(f"{best_snippet}")
            else:
                response_parts.append(text)
            
            response_parts.append("")
    
    if web_results and not video_results:
        response_parts.append("بناءً على البحث في الإنترنت:")
        
        for i, result in enumerate(web_results[:2], 1):
            response_parts.append(f"\n🌐 **{result.get('title', 'مصدر ويب')}**")
            response_parts.append(result['snippet'])
            response_parts.append("")
    
    if not video_results and not web_results:
        response_parts.append("عذراً، لم أجد معلومات متعلقة بسؤالك في محتوى الفيديو أو الإنترنت.")
        response_parts.append("\n💡 نصائح للحصول على نتائج أفضل:")
        response_parts.append("• استخدم كلمات مختلفة أو مرادفات")
        response_parts.append("• اطرح أسئلة أكثر تحديداً")
        response_parts.append("• جرب السؤال باللغة العربية إذا كان متعلقاً بالفيديو")
    
    full_text = "\n".join(response_parts)
    
    # Format with proper Arabic direction
    formatted_text = f'<div class="arabic-text">{full_text}</div>'
    return formatted_text

# --- Load transcriptions ---
if not st.session_state.transcriptions_loaded:
    with st.spinner("📁 Loading video transcriptions..."):
        st.session_state.transcriptions_data = load_transcriptions()
        st.session_state.transcriptions_loaded = True
        
        if st.session_state.transcriptions_data:
            total_words = sum(t["word_count"] for t in st.session_state.transcriptions_data)
            st.success(f"✅ Loaded {len(st.session_state.transcriptions_data)} transcription files ({total_words:,} words total)")
        else:
            st.warning("⚠️ No transcription files found in ./transcriptions folder")

# --- Main App ---
# Header
st.markdown('<h1 class="main-header">🎥 Video Chat Assistant</h1>', unsafe_allow_html=True)

# Success message
if st.session_state.transcriptions_data:
    st.markdown(f"""
    <div class="success-box">
        <strong>✅ App is ready!</strong><br>
        📁 Loaded {len(st.session_state.transcriptions_data)} transcription files<br>
        🌐 Web search {'✅ available' if WEB_SEARCH_AVAILABLE else '❌ not available'}
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
    st.markdown("### 📊 System Status")
    st.write(f"💬 Total messages: {len(st.session_state.messages)}")
    st.write(f"📁 Video files: {len(st.session_state.transcriptions_data)} loaded")
    st.write(f"🌐 Web search: {'✅ Available' if WEB_SEARCH_AVAILABLE else '❌ Not available'}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.success("Chat cleared!")
        st.rerun()
    
    # Test search button
    if st.button("🔍 Test Search", use_container_width=True):
        if st.session_state.transcriptions_data:
            test_query = "المناعة في النبات"
            results = smart_text_search(test_query, st.session_state.transcriptions_data, top_k=2)
            st.write(f"Test query: '{test_query}'")
            st.write(f"Found {len(results)} results")
            for i, r in enumerate(results):
                st.write(f"{i+1}. {r['metadata']['source']} (score: {r['score']:.3f})")
        else:
            st.error("No transcriptions loaded")
    
    # Instructions
    st.markdown("### 📝 How to use")
    st.markdown("""
    1. **Watch the video** on the left
    2. **Ask questions** about the content in Arabic or English
    3. **Get answers** from video transcriptions or web
    4. **No AI setup required** - works with text search
    """)
    
    st.markdown("### 💡 Example questions")
    st.markdown("""
    - ما هي المناعة في النبات؟
    - شرح المناعة التركيبية
    - What is plant immunity?
    - البروتينات المضادة للميكروبات
    """)

# Main content layout
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### 🎥 Educational Video")
    
    # Video container
    st.markdown('<div class="video-container">', unsafe_allow_html=True)
    st.video("https://youtu.be/4oaHltuDrL8")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("**Video:** Plant Immunity Education")
    
    # Video information
    with st.expander("📋 About this video"):
        if st.session_state.transcriptions_data:
            total_words = sum(t["word_count"] for t in st.session_state.transcriptions_data)
            st.write(f"""
            This educational video has been transcribed into {len(st.session_state.transcriptions_data)} text files 
            containing {total_words:,} words total. The app can search through this content to answer your questions
            about plant immunity and related topics discussed in the video.
            
            **Content includes:** Plant immunity mechanisms, biochemical defense systems, and educational explanations in Arabic.
            """)
        else:
            st.write("Transcription files not found. Please ensure the ./transcriptions folder contains the video transcripts.")

with col2:
    st.markdown("### 💬 Smart Chat Assistant")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                # Show source indicator for assistant messages
                if message["role"] == "assistant" and "source" in message:
                    if message["source"] == "video":
                        st.markdown('<div class="source-indicator video-source">🎥 From Video Transcription</div>', 
                                  unsafe_allow_html=True)
                    elif message["source"] == "web":
                        st.markdown('<div class="source-indicator web-source">🌐 From Web Search</div>', 
                                  unsafe_allow_html=True)
                    elif message["source"] == "simple":
                        st.markdown('<div class="source-indicator simple-source">🔍 From Video Content</div>', 
                                  unsafe_allow_html=True)
                
                st.markdown(message["content"], unsafe_allow_html=True)
                
                # Show sources if available
                if message["role"] == "assistant" and "sources" in message and message["sources"]:
                    with st.expander("📚 Sources & Details", expanded=False):
                        if message.get("source") == "video" or message.get("source") == "simple":
                            for i, source in enumerate(message["sources"], 1):
                                st.write(f"**File:** {source.get('metadata', {}).get('source', 'Unknown')}")
                                st.write(f"**Words:** {source.get('word_count', 'Unknown')}")
                                if i < len(message["sources"]):
                                    st.divider()
                        else:  # web sources
                            for i, result in enumerate(message["sources"], 1):
                                st.markdown(f"**{i}.** [{result.get('title', 'Web Source')}]({result.get('href', '#')})")

    # Chat input
    if not st.session_state.processing:
        if prompt := st.chat_input("Ask about the video content or any topic..."):
            st.session_state.processing = True
            
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

            # Generate response
            with st.spinner("🔍 Searching..."):
                # Search video transcriptions first
                video_results = []
                if st.session_state.transcriptions_data:
                    video_results = smart_text_search(prompt, st.session_state.transcriptions_data, top_k=3)
                
                # Search web if no good video results
                web_results = []
                if not video_results and WEB_SEARCH_AVAILABLE:
                    with st.spinner("🌐 Searching the web..."):
                        web_results = search_web(prompt, max_results=3)
                
                # Generate response
                assistant_response = generate_response(prompt, video_results, web_results)
                
                # Determine source and prepare data
                if video_results:
                    source = "video"
                    sources = video_results
                    status_msg = '<div class="arabic-text">✅ **من محتوى الفيديو**</div>'
                    full_response = f"{assistant_response}\n\n{status_msg}"
                elif web_results:
                    source = "web"
                    sources = web_results
                    status_msg = '<div class="arabic-text">🌐 **من البحث على الإنترنت**</div>'
                    full_response = f"{assistant_response}\n\n{status_msg}"
                else:
                    source = "none"
                    sources = []
                    full_response = assistant_response

            # Display response with typing effect
            with chat_container:
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    
                    # For HTML content, display directly without typing effect
                    if '<div class="arabic-text">' in full_response:
                        message_placeholder.markdown(full_response, unsafe_allow_html=True)
                    else:
                        # Typing effect for plain text
                        displayed_response = ""
                        for chunk in full_response.split():
                            displayed_response += chunk + " "
                            time.sleep(0.03)
                            message_placeholder.markdown(displayed_response + "▌")
                        message_placeholder.markdown(full_response)

            # Save message to session state
            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_response,
                "source": source,
                "sources": sources
            })
            
            st.session_state.processing = False
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    🎥 Video Chat Assistant - Smart text search without AI models | 
    Works with video transcriptions and web search
</div>
""", unsafe_allow_html=True)
