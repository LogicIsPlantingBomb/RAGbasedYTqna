import streamlit as st
import re
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableParallel
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import TranscriptsDisabled, VideoUnavailable
from langchain_community.vectorstores import FAISS
import time

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="YouTube Q&A Assistant",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #0f1419;
        color: #e6e6e6;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
    }
    
    .stTextInput > div > div > input {
        background-color: #1e2329;
        color: #e6e6e6;
        border: 1px solid #3d4852;
        border-radius: 8px;
    }
    
    .stSelectbox > div > div > select {
        background-color: #1e2329;
        color: #e6e6e6;
        border: 1px solid #3d4852;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .status-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        background-color: rgba(102, 126, 234, 0.1);
    }
    
    .error-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #ff6b6b;
        background-color: rgba(255, 107, 107, 0.1);
        color: #ff6b6b;
    }
    
    .success-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #4ecdc4;
        background-color: rgba(78, 205, 196, 0.1);
        color: #4ecdc4;
    }
    
    .sidebar .stSelectbox > div > div > select {
        background-color: #1e2329;
        color: #e6e6e6;
    }
    
    .processing-animation {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #667eea;
    }
    
    .spinner {
        width: 20px;
        height: 20px;
        border: 2px solid #3d4852;
        border-top: 2px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .step-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 6px;
        background-color: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        margin: 5px 0;
    }
    
    .step-number {
        background: #667eea;
        color: white;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def extract_video_id(url_or_id):
    """Extract video ID from YouTube URL or return the ID if already provided"""
    if not url_or_id:
        return None
    
    # If it's already just an ID (11 characters, alphanumeric)
    if len(url_or_id) == 11 and url_or_id.isalnum():
        return url_or_id
    
    # Extract from various YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    return None

def format_docs(retrieved_docs):
    """Format retrieved documents into context text"""
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
    return context_text

def show_processing_step(description, is_completed=False):
    """Show processing step with tick when completed"""
    if is_completed:
        st.markdown(f"""
        <div class="step-indicator">
            <div class="step-number">✓</div>
            <span>{description}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="step-indicator">
            <div class="spinner"></div>
            <span>{description}</span>
        </div>
        """, unsafe_allow_html=True)

# Sidebar with instructions
with st.sidebar:
    st.title("📝 Instructions")
    
    st.markdown("""
    ### How to Use:
    
    1. **Enter Video URL or ID**
       - Paste full YouTube URL or just the video ID
       - Supports all YouTube URL formats
    
    2. **Select Language**
       - Choose subtitle language
       - English is default and most common
    
    3. **Ask Your Question**
       - Be specific about what you want to know
       - Questions are answered from video content only
    
    4. **Get Answers**
       - AI analyzes transcript and provides relevant answers
       - Processing takes 10-30 seconds depending on video length
    
    ### Supported Languages:
    - English (en)
    - Spanish (es)  
    - French (fr)
    - German (de)
    - Italian (it)
    - Portuguese (pt)
    - Russian (ru)
    - Japanese (ja)
    - Korean (ko)
    - Chinese (zh)
    """)
    
    st.markdown("---")
    st.markdown("**Note:** Only videos with available subtitles can be processed.")

# Main interface
st.title("🎥 YouTube Transcript Q&A Assistant")
st.markdown("Ask questions about any YouTube video content using AI-powered analysis")

# Input section
col1, col2 = st.columns([2, 1])

with col1:
    video_input = st.text_input(
        "YouTube URL or Video ID",
        placeholder="https://youtube.com/watch?v=... or just the video ID",
        help="Paste the full YouTube URL or just the 11-character video ID"
    )

with col2:
    language_options = {
        'English': 'en',
        'Spanish': 'es', 
        'French': 'fr',
        'German': 'de',
        'Italian': 'it',
        'Portuguese': 'pt',
        'Russian': 'ru',
        'Japanese': 'ja',
        'Korean': 'ko',
        'Chinese': 'zh'
    }
    
    selected_language = st.selectbox(
        "Subtitle Language",
        options=list(language_options.keys()),
        index=0,
        help="Select the language for video subtitles"
    )

question = st.text_input(
    "Your Question",
    placeholder="What is this video about? What are the main points discussed?",
    help="Ask any question about the video content"
)

# Process button
if st.button("🚀 Get Answer", type="primary"):
    if not video_input or not question:
        st.markdown('<div class="error-box">⚠️ Please provide both a YouTube URL/ID and a question.</div>', unsafe_allow_html=True)
    else:
        # Extract video ID
        video_id = extract_video_id(video_input)
        
        if not video_id:
            st.markdown('<div class="error-box">❌ Invalid YouTube URL or video ID. Please check your input.</div>', unsafe_allow_html=True)
        else:
            # Processing section
            st.markdown("### 🔄 Processing...")
            
            # Create placeholders for each step
            step1_placeholder = st.empty()
            step2_placeholder = st.empty()
            step3_placeholder = st.empty()
            step4_placeholder = st.empty()
            
            try:
                # Step 1: Fetch transcript
                with step1_placeholder:
                    show_processing_step("Fetching video transcript...")
                
                ytt_api = YouTubeTranscriptApi()
                language_code = language_options[selected_language]
                
                try:
                    fetched_transcript = ytt_api.fetch(video_id, languages=[language_code])
                except:
                    # Fallback to English if selected language is not available
                    fetched_transcript = ytt_api.fetch(video_id, languages=['en'])
                    st.warning(f"⚠️ {selected_language} subtitles not available. Using English instead.")
                
                transcript = " ".join(snippet.text for snippet in fetched_transcript)
                
                # Update step 1 as completed
                with step1_placeholder:
                    show_processing_step("Transcript fetched ✓", True)
                
                # Step 2: Split text
                with step2_placeholder:
                    show_processing_step("Splitting transcript into chunks...")
                
                splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                chunks = splitter.create_documents([transcript])
                
                # Update step 2 as completed
                with step2_placeholder:
                    show_processing_step(f"Text chunks created ({len(chunks)} chunks) ✓", True)
                
                # Step 3: Create embeddings
                with step3_placeholder:
                    show_processing_step("Creating vector embeddings...")
                
                embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
                vector_store = FAISS.from_documents(chunks, embeddings)
                
                # Update step 3 as completed
                with step3_placeholder:
                    show_processing_step("Vector embeddings created ✓", True)
                
                # Step 4: Generate answer
                with step4_placeholder:
                    show_processing_step("Generating AI response...")
                
                parser = StrOutputParser()
                retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
                
                prompt = PromptTemplate(
                    template="""
                    You are a helpful assistant analyzing YouTube video content.
                    Answer the question based ONLY on the provided transcript context.
                    If the context doesn't contain sufficient information, politely say you don't know.
                    Provide detailed, well-structured answers when possible.
                    
                    Context from video transcript:
                    {context}
                    
                    Question: {question}
                    
                    Answer:
                    """,
                    input_variables=['context', 'question']
                )
                
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)
                
                parallel_chain = RunnableParallel({
                    'context': retriever | RunnableLambda(format_docs),
                    'question': RunnablePassthrough()
                })
                
                main_chain = parallel_chain | prompt | llm | parser
                response = main_chain.invoke(question)
                
                # Update step 4 as completed
                with step4_placeholder:
                    show_processing_step("AI response generated ✓", True)
                
                # Add a small delay to show all completed steps
                time.sleep(1)
                
                # Success message
                st.markdown('<div class="success-box">🎉 Processing completed successfully!</div>', unsafe_allow_html=True)
                
                # Display results
                st.markdown("### 💬 Answer")
                st.markdown(f"**Question:** {question}")
                st.markdown("**Response:**")
                st.write(response)
                
                # Video info
                with st.expander("📊 Processing Details"):
                    st.write(f"**Video ID:** {video_id}")
                    st.write(f"**Language:** {selected_language}")
                    st.write(f"**Transcript Length:** {len(transcript)} characters")
                    st.write(f"**Text Chunks:** {len(chunks)}")
                
            except TranscriptsDisabled:
                # Clear all placeholders
                step1_placeholder.empty()
                step2_placeholder.empty() 
                step3_placeholder.empty()
                step4_placeholder.empty()
                st.markdown('<div class="error-box">❌ No subtitles available for this video. Please try a video with captions enabled.</div>', unsafe_allow_html=True)
                
            except VideoUnavailable:
                # Clear all placeholders
                step1_placeholder.empty()
                step2_placeholder.empty()
                step3_placeholder.empty() 
                step4_placeholder.empty()
                st.markdown('<div class="error-box">❌ Video is unavailable or private. Please check the URL and try again.</div>', unsafe_allow_html=True)
                
            except Exception as e:
                # Clear all placeholders
                step1_placeholder.empty()
                step2_placeholder.empty()
                step3_placeholder.empty()
                step4_placeholder.empty()
                st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("*Powered by Google Gemini AI and LangChain*")
