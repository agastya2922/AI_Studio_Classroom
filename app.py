import streamlit as st
import os
import gc
import json
# PyMuPDF is optional until a PDF is uploaded. Import it dynamically so the
# app can still start in environments where the package is not installed.
try:
    import importlib
    fitz = importlib.import_module("fitz")
except ImportError:
    fitz = None
# Keep the app usable when the optional `python-dotenv` package is not installed.
def load_dotenv(dotenv_path=".env"):
    """Load simple KEY=VALUE entries from a local .env file if present."""
    if not os.path.isfile(dotenv_path):
        return
    with open(dotenv_path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
# Load the optional Mistral integration dynamically so the app can still start
# in environments where the package has not been installed yet.
try:
    _mistral = importlib.import_module("langchain_mistralai")
    MistralAIEmbeddings = _mistral.MistralAIEmbeddings
    ChatMistralAI = _mistral.ChatMistralAI
except ImportError:
    MistralAIEmbeddings = None
    ChatMistralAI = None
# Chroma was moved to the dedicated `langchain-chroma` package. Keep a
# fallback for environments that still have the older LangChain integration.
try:
    Chroma = importlib.import_module("langchain_chroma").Chroma
except ImportError:
    Chroma = importlib.import_module("langchain_community.vectorstores").Chroma
# Load LangChain classes dynamically so static analysis and older installations
# without `langchain-core` do not prevent the app from starting.
try:
    _langchain_core = importlib.import_module("langchain_core")
    ChatPromptTemplate = importlib.import_module(
        "langchain_core.prompts"
    ).ChatPromptTemplate
    Document = importlib.import_module("langchain_core.documents").Document
except ImportError:
    # Compatibility with older LangChain installations.
    ChatPromptTemplate = importlib.import_module(
        "langchain.prompts"
    ).ChatPromptTemplate
    Document = importlib.import_module("langchain.schema").Document
try:
    RecursiveCharacterTextSplitter = importlib.import_module(
        "langchain_text_splitters"
    ).RecursiveCharacterTextSplitter
except ImportError:
    # Compatibility with older LangChain installations.
    RecursiveCharacterTextSplitter = importlib.import_module(
        "langchain.text_splitter"
    ).RecursiveCharacterTextSplitter
# ChromaDB is only required when a document is uploaded. Keep startup working
# in environments where the optional package is not installed.
try:
    chromadb = importlib.import_module("chromadb")
except ImportError:
    chromadb = None

# Initialize Environment
load_dotenv()

st.set_page_config(page_title="Mr. AI's Study Classroom 👨‍🏫", page_icon="🍎", layout="wide")

# ----------------- CUSTOM STYLE INJECTIONS (School Blackboard & Notebook Theme) -----------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Architects+Daughter&family=Comfortaa:wght@400;700&family=Playfair+Display:ital,wght@0,600;0,800;1,500&family=Short+Stack&family=Schoolbell&family=Kalam:wght@400;700&display=swap" rel="stylesheet">
<style>
.stApp { background-color: #fdfbf7; background-image: radial-gradient(#ece7da 8%, transparent 8%), radial-gradient(#ece7da 8%, transparent 8%); background-size: 20px 20px; background-position: 0 0, 10px 10px; }
.chalkboard { background: radial-gradient(circle, #224d36 0%, #163223 100%); border: 10px solid #5c4033; border-radius: 8px; padding: 20px; color: #f5f5f5; font-family: 'Playfair Display', serif; text-align: center; box-shadow: 0 8px 16px rgba(0,0,0,0.25), inset 0 0 50px rgba(0,0,0,0.7); margin-bottom: 25px; }
.chalkboard h1 { font-family: 'Playfair Display', serif; color: #fff !important; text-shadow: 2px 2px 0px rgba(0,0,0,0.4); margin: 0; font-size: 2.3rem; font-weight: bold; }
.chalkboard p { font-size: 1.1rem; color: #d1ebd9 !important; font-family: 'Comfortaa', sans-serif; }
[data-testid="stSidebar"] { background-color: #162f21 !important; border-right: 4px solid #4d3319; }
[data-testid="stSidebar"] * { color: #eceee8 !important; font-family: 'Comfortaa', sans-serif !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #ffeb3b !important; font-family: 'Playfair Display', serif !important; font-weight: bold !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] li, [data-testid="stSidebar"] label { color: #eceee8 !important; font-family: 'Comfortaa', sans-serif !important; }
[data-testid="stSidebar"] b { color: #fffdf5 !important; }
.notebook-paper { background: #fff; border: 1px solid #e0dfdb; border-left: 3px double #ff6666; padding: 25px 25px 25px 35px; font-family: 'Comfortaa', sans-serif; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-radius: 6px; margin-bottom: 20px; line-height: 1.6; }
.notebook-paper h2, .notebook-paper h3 { font-family: 'Playfair Display', serif; color: #7b1113 !important; border-bottom: 2px dashed #e0dfdb; padding-bottom: 5px; margin-top: 0; }
.grade-stamp { border: 4px double #d32f2f !important; border-radius: 50%; width: 105px; height: 105px; display: inline-flex; flex-direction: column; align-items: center; justify-content: center; font-family: 'Playfair Display', serif; font-weight: 800; font-size: 1.9rem; color: #d32f2f !important; transform: rotate(-12deg); margin: 10px auto; background-color: rgba(255,235,235,0.3); }
.grade-stamp span { font-size: 0.65rem; text-transform: uppercase; margin-bottom: -4px; color: #d32f2f !important; }
.question-block { background-color: #f7f9fa; border-left: 4px solid #f39c12; padding: 12px 18px; margin: 12px 0; border-radius: 4px; font-family: 'Comfortaa', sans-serif; color: #3b2f21 !important; }
.bubble-teacher { background: #f6f3eb; border: 2px solid #8c7355; border-radius: 10px; padding: 12px; margin: 8px 0; font-family: 'Comfortaa', sans-serif; color: #3b2f21 !important; }
.bubble-student { background: #e6f2ff; border: 2px solid #5fa4e6; border-radius: 10px; padding: 12px; margin: 8px 0 8px auto; text-align: right; font-family: 'Comfortaa', sans-serif; color: #1a2a3a !important; max-width: 85%; }
div.stButton > button { background-color: #1e3f2c !important; color: #fff !important; border: 3px solid #6d4c41 !important; border-radius: 6px !important; font-family: 'Playfair Display', serif !important; font-size: 1.1rem !important; font-weight: bold !important; }
div.stButton > button:hover { background-color: #28543b !important; transform: translateY(-1px); }
.correction-success { color: #2e7d32; padding: 6px; border-radius: 4px; font-size: 0.9rem; background-color: #e8f5e9; border: 1px solid #a5d6a7; margin-top: 5px; font-family: 'Comfortaa', sans-serif; }
.correction-wrong { color: #c62828; padding: 6px; border-radius: 4px; font-size: 0.9rem; background-color: #ffebee; border: 1px solid #ffcdd2; margin-top: 5px; font-family: 'Comfortaa', sans-serif; }
.notebook-paper * { color: #3b2f21 !important; }
.notebook-paper h2, .notebook-paper h3, .notebook-paper h2 *, .notebook-paper h3 * { color: #7b1113 !important; }
.question-block { color: #3e2723 !important; }
.question-block * { color: #3e2723 !important; }
.correction-success * { color: #2e7d32 !important; }
.correction-wrong * { color: #c62828 !important; }
.stAppViewMain div[data-testid="stRadio"] label p { color: #3b2f21 !important; font-family: 'Comfortaa', sans-serif !important; }
div[data-testid="stAlert"] * { color: #5c3e15 !important; font-family: 'Comfortaa', sans-serif !important; }
.stAppViewMain div.stMarkdown p { color: #3b2f21 !important; font-family: 'Comfortaa', sans-serif !important; }
span[data-testid="stHeaderActionActiveText"] { color: #7b1113 !important; }
.stAppViewMain h1, .stAppViewMain h2, .stAppViewMain h3 { color: #5c4033 !important; }
.stAppViewMain p, .stAppViewMain span, .stAppViewMain label, .stAppViewMain li { color: #3b2f21 !important; font-family: 'Comfortaa', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

# ----------------- PARSING & LLM HELPERS -----------------
def inspect_pdf_pages(file_bytes):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        return len(doc)
    except:
        return 0

def process_pdf_pages(file_bytes, page_range):
    docs = []
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for idx in range(max(0, page_range[0]), min(len(doc), page_range[1] + 1)):
            text = doc.load_page(idx).get_text()
            if text.strip():
                docs.append(Document(page_content=text, metadata={"source": "uploaded_book", "page": idx + 1}))
        return docs
    except Exception as e:
        st.error(f"Error PDF: {e}")
        return []

def process_non_pdf(file_bytes, file_name):
    docs = []
    file_ext = os.path.splitext(file_name)[1].lower()
    try:
        if file_ext == ".docx":
            import io
            import zipfile
            import xml.etree.ElementTree as ET

            with zipfile.ZipFile(io.BytesIO(file_bytes)) as archive:
                document_xml = archive.read("word/document.xml")
            root = ET.fromstring(document_xml)
            namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            paragraphs = []
            for paragraph in root.iter(f"{namespace}p"):
                text = "".join(node.text or "" for node in paragraph.iter(f"{namespace}t"))
                if text.strip():
                    paragraphs.append(text)
            text_content = "\n".join(paragraphs)
            docs = [Document(page_content=text_content, metadata={"source": file_name})]
        elif file_ext in [".txt", ".md"]:
            text_content = file_bytes.decode("utf-8", errors="ignore")
            docs = [Document(page_content=text_content, metadata={"source": file_name})]
        return docs
    except Exception as e:
        st.error(f"Error parsing: {e}")
        return []

def get_llm():
    return ChatMistralAI(model="mistral-small-2506", temperature=0.2)

def generate_quiz_mcqs(num_questions=5, difficulty="Intermediate", student_type="School Student"):
    if not st.session_state.loaded_chunks:
        return None
    chunks = st.session_state.loaded_chunks
    total = len(chunks)
    chunks_to_sample = min(total, max(5, num_questions))
    
    if total <= chunks_to_sample:
        sampled_chunks = chunks
    else:
        indices = [int(i * (total - 1) / (chunks_to_sample - 1)) for i in range(chunks_to_sample)] if chunks_to_sample > 1 else [0]
        sampled_chunks = [chunks[idx] for idx in sorted(list(set(indices)))]
        
    context_text = "\n\n".join([f"--- EXCERPT {idx+1} (Source page: {c.metadata.get('page', 'Book')}) ---\n{c.page_content}" for idx, c in enumerate(sampled_chunks)])
    
    quiz_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are Mr. AI, a helpful, traditional teacher. Write exactly {num_questions} multiple choice questions (MCQs) for a pop quiz based ONLY on the provided textbook excerpts.
Rules:
1. Questions must be answerable ONLY from the excerpts. Do not use outside knowledge.
2. Question difficulty: {difficulty} Level (Beginner = recall facts, Intermediate = explain concepts, Advanced = synthesis and logical comparison).
3. Student grade: {student_type} Level (vocabulary and complexity matching {student_type} curriculum).
4. Each question must have exactly 4 choices.
5. Set correct_index to the correct answer index (0 to 3).
6. Provide a short 'explanation' from text.
7. Return raw JSON matching this schema: Your output must be a single JSON object with a 'questions' key. The value of 'questions' must be an array of question objects. Each question object contains the keys 'question' (string), 'options' (array of 4 strings), 'correct_index' (integer 0-3), and 'explanation' (string)."""),
        ("human", "Text book excerpts:\n{text_context}\n\nDeliver JSON object now:")
    ])
    
    # Enforce JSON object response format
    llm = ChatMistralAI(model="mistral-small-2506", temperature=0.2, response_format={"type": "json_object"})
    with st.spinner("👨‍🏫 Mr. AI is writing down the test questions on the chalkboard..."):
        try:
            res = llm.invoke(quiz_prompt.format_messages(text_context=context_text))
            res_content = res.content.strip()
            parsed = json.loads(res_content)
            if "questions" in parsed:
                return parsed["questions"][:num_questions]
            elif isinstance(parsed, list):
                return parsed[:num_questions]
            else:
                st.error("❌ The generated quiz was in an unexpected format. Please try again.")
                return None
        except Exception as e:
            st.error(f"❌ Failed to build pop quiz: {e}")
            return None

# ----------------- SESSION STATE VALUES -----------------
for key in ["db", "uploaded_file_name_key", "loaded_chunks", "quiz", "quiz_answers", "quiz_graded", "chat_history", "student_type"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "quiz_graded" and key != "quiz_answers" and key != "loaded_chunks" and key != "chat_history" else ([] if key != "quiz_answers" and key != "quiz_graded" else ({} if key == "quiz_answers" else False))
if not st.session_state.student_type:
    st.session_state.student_type = "School Student"

# Chalkboard Title
st.markdown('<div class="chalkboard"><h1>Mr. AI\'s Studio Classroom 👨‍🏫</h1><p>🍏 "Quiet down, Class! Upload your study book, choose your options, and let\'s get learning." 🍏</p></div>', unsafe_allow_html=True)

# ----------------- SIDEBAR: Blackboard Class Info -----------------
with st.sidebar:
    st.markdown("<div style='text-align: center; margin-top: 10px; margin-bottom: 25px;'><span style='font-size: 4.5rem;'>👨‍🏫</span><h2 style='color: #ffeb3b; font-family: \"Playfair Display\", serif; margin: 5px 0;'>Mr. AI's Desk</h2><p style='color: #d1ebd9; font-style: italic; font-size: 0.95rem; font-family: \"Comfortaa\", sans-serif;'>\"Attention, Class! Keep your desk clean, study your slides, and complete your homework exercises.\"</p></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px dashed #5c4033;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #ffb74d; font-family: \"Playfair Display\", serif;'>📊 Blackboard Stats</h3>", unsafe_allow_html=True)
    if st.session_state.uploaded_file_name_key:
        fname = st.session_state.uploaded_file_name_key.split("_range_")[0]
        st.markdown(f"<div style='background-color: rgba(255,255,255,0.08); padding: 12px; border-radius: 6px; font-family: \"Comfortaa\", sans-serif;'>📄 <b>Active Book:</b><br><span style='color: #81c784;'>{fname}</span><br><br>📝 <b>Study Cards:</b> <span style='color: #81c784;'>{len(st.session_state.loaded_chunks)}</span> in RAM<br></div>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-style: italic; color: #ffab91; font-family: \"Comfortaa\", sans-serif;'>No book active on the desk.</p>", unsafe_allow_html=True)
        
    st.markdown("<hr style='border: 1px dashed #5c4033;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #ffb74d; font-family: \"Playfair Display\", serif;'>🪵 Class Directives</h3>", unsafe_allow_html=True)
    st.markdown("<ul style='font-family: \"Comfortaa\", sans-serif; padding-left: 20px; color: #e8f5e9; font-size: 0.95rem; line-height: 1.5;'><li><b>Textbook Lockdown:</b> Mr. AI answers questions strictly from textbook pages. No outside knowledge.</li><li><b>Pop Quiz Generator:</b> Custom build 3 to 15 questions based on Beginner, Intermediate, or Advanced level settings.</li><li><b>No Leakage:</b> Every time you hand in a new book, the older files are immediately deleted from memory.</li></ul>", unsafe_allow_html=True)

# ----------------- MAIN UI: HOMEWORK DESK UPLOADER (Highly Visible) -----------------
st.markdown('<div class="notebook-paper">', unsafe_allow_html=True)
st.markdown('<h2>📚 Mr. AI\'s Homework Desk</h2>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "📂 Hand in your textbook here (PDF, DOCX, or TXT):", 
    type=["pdf", "docx", "txt"],
    help="Upload book. Uploading a book instantly clears other book cache from RAM."
)

if uploaded_file:
    file_name = uploaded_file.name
    is_pdf = file_name.lower().endswith(".pdf")
    file_bytes = uploaded_file.read()
    uploaded_file.seek(0)
    col_file_info, col_academic_opts = st.columns([3, 2])
    with col_file_info:
        st.markdown(f"<div style='background-color: #f7f9fa; border-left: 4px solid #7b1113; padding: 10px 15px; border-radius: 4px; margin-bottom: 10px;'>📄 <b>Handed In:</b> {file_name}</div>", unsafe_allow_html=True)
        if st.button("❌ Remove Book", help="Erase all book memory immediately."):
            for k in ["db", "uploaded_file_name_key", "loaded_chunks", "quiz", "quiz_answers", "quiz_graded", "chat_history"]:
                st.session_state[k] = [] if k in ["loaded_chunks", "chat_history"] else ({} if k == "quiz_answers" else (False if k == "quiz_graded" else None))
            gc.collect()
            st.rerun()
            
    with col_academic_opts:
        st.session_state.student_type = st.selectbox(
            "🎓 Select Academic Level:",
            options=["School Student", "College Student"],
            index=0 if st.session_state.student_type == "School Student" else 1,
            help="Tailor vocabulary and complexity matching School or College student levels."
        )

    if is_pdf:
        tot_pages = inspect_pdf_pages(file_bytes)
        if tot_pages > 1:
            study_range = st.slider(
                "📚 Select Page Range to study:",
                min_value=1,
                max_value=tot_pages,
                value=(1, min(tot_pages, 10)),
                help="Determine which pages of the book to register in vector store."
            )
            # PyMuPDF is imported at startup when available.
        else:
            study_range = (1, 1)
            st.info("📚 Single page document. Entire document will be registered.")
        range_key = f"{file_name}_range_{study_range[0]}_{study_range[1]}_{st.session_state.student_type}"
    else:
        range_key = f"{file_name}_{st.session_state.student_type}"
        study_range = (1, 1)
        
    # Process and embed if new selection
    if st.session_state.uploaded_file_name_key != range_key:
        with st.status("🧹 Clearing desk and setting up study cards...", expanded=True) as status:
            for k in ["db", "loaded_chunks", "quiz", "quiz_answers", "quiz_graded", "chat_history"]:
                st.session_state[k] = [] if k in ["loaded_chunks", "chat_history"] else ({} if k == "quiz_answers" else (False if k == "quiz_graded" else None))
            gc.collect()
            
            docs = process_pdf_pages(file_bytes, (study_range[0]-1, study_range[1]-1)) if is_pdf else process_non_pdf(file_bytes, file_name)
            if docs:
                if chromadb is None:
                    status.update(label="❌ ChromaDB is not installed. Install 'chromadb' to process documents.", state="error")
                    st.session_state.uploaded_file_name_key = None
                    st.stop()
                splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
                st.session_state.loaded_chunks = splitter.split_documents(docs)
                
                embeddings = MistralAIEmbeddings()
                client = chromadb.EphemeralClient()
                st.session_state.db = Chroma.from_documents(documents=st.session_state.loaded_chunks, embedding=embeddings, client=client)
                st.session_state.uploaded_file_name_key = range_key
                status.update(label="✏️ New textbook registered! Ready to study.", state="complete")
            else:
                status.update(label="❌ Read error. Could not extract text from document.", state="error")
                st.session_state.uploaded_file_name_key = None
else:
    for k in ["db", "uploaded_file_name_key", "loaded_chunks", "quiz", "quiz_answers", "quiz_graded", "chat_history"]:
        st.session_state[k] = [] if k in ["loaded_chunks", "chat_history"] else ({} if k == "quiz_answers" else (False if k == "quiz_graded" else None))
    gc.collect()
    st.markdown('<div style="background-color: #fffde7; border: 4px dashed #f57f17; padding: 25px; border-radius: 12px; text-align: center; margin-top: 15px;"><span style="font-size: 3.5rem;">🎒</span><h3 style="font-family: \'Playfair Display\', serif; color: #e65100; margin-top: 10px;">Mr. AI\'s Desk: Drop Your Homework Here!</h3><p style="font-family: \'Comfortaa\', cursive; color: #5d4037; font-size: 1rem; max-width: 600px; margin: 10px auto;">Please upload a schoolbook above to begin lessons. Mr. AI will convert the pages in-memory instantly!</p></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ----------------- TABS WORKSPACE -----------------
tab1, tab2 = st.tabs(["💬 Ask The Teacher", "✍️ Take Pop Quiz"])

# ----- TAB 1: RAG Q&A -----
with tab1:
    st.markdown('<div class="notebook-paper"><h2>📋 Lesson Question & Answer Board</h2><p style="color: #666; font-style: italic;">Ask questions based only on your uploaded materials. Mr. AI will reply matching a <b>' + st.session_state.student_type + '</b> tier.</p></div>', unsafe_allow_html=True)
    if not st.session_state.db:
        st.warning("📚 Please upload a textbook above first before starting the lesson!")
    else:
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.markdown(f'<div class="bubble-student"><b>You:</b> {chat["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bubble-teacher"><b>Mr. AI:</b> {chat["content"]}</div>', unsafe_allow_html=True)
        
        with st.form("classroom_chat_form", clear_on_submit=True):
            user_q = st.text_input("Ask a question about the book:", placeholder="e.g. What is the main thesis of chapter 1?")
            submit_q = st.form_submit_button("💬 Ask Mr. AI")
            
        if submit_q and user_q:
            st.markdown(f'<div class="bubble-student"><b>You:</b> {user_q}</div>', unsafe_allow_html=True)
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            
            db = st.session_state.db
            retriever = db.as_retriever(search_kwargs={"k": 4})
            docs = retriever.invoke(user_q)
            context_str = "\n\n".join([f"--- Page {d.metadata.get('page', 'unknown')} ---\n{d.page_content}" for d in docs])
            
            teacher_prompt = ChatPromptTemplate.from_messages([
                ("system", f"""You are Mr. AI, a strict, encouraging school teacher. Answer the student's question based ONLY on the provided textbook context. Do not use outside facts.
Guidelines:
1. Quote or refer to details directly from the textbook text.
2. Explain in a style suitable for a {st.session_state.student_type} (vocabulary, details, depth matching {st.session_state.student_type} curriculums).
3. If the answer is NOT present in the textbook context, you MUST state exactly: "I could not find the answer in the document." Do not try to guess or use general knowledge."""),
                ("human", "Textbook Context:\n{context}\n\nStudent Question:\n{question}")
            ])
            
            llm = get_llm()
            with st.spinner("👨‍🏫 Mr. AI is fetching her classroom notes..."):
                try:
                    response = llm.invoke(teacher_prompt.format_messages(context=context_str, question=user_q))
                    st.markdown(f'<div class="bubble-teacher"><b>Mr. AI:</b> {response.content}</div>', unsafe_allow_html=True)
                    st.session_state.chat_history.append({"role": "teacher", "content": response.content})
                except Exception as e:
                    st.error(f"Error calling AI Teacher: {e}")

# ----- TAB 2: POP QUIZ -----
with tab2:
    st.markdown('<div class="notebook-paper"><h2>✏️ Hand-Written Pop Quiz Room</h2><p style="color: #666; font-style: italic;">Complete this quiz to test your memory of the homework. Mr. AI will grade your answers at the end!</p></div>', unsafe_allow_html=True)
    if not st.session_state.db:
        st.warning("📚 Please upload a textbook above first to draft a quiz!")
    else:
        if not st.session_state.quiz:
            st.markdown('<div class="notebook-paper"><h3>📝 Create Test Sheet:</h3>', unsafe_allow_html=True)
            col_qty, col_diff = st.columns(2)
            with col_qty:
                quiz_qty = st.slider("✏️ Select Question Count:", min_value=3, max_value=15, value=5, step=1)
            with col_diff:
                quiz_diff = st.selectbox("⚡ Difficulty Mode:", options=["Beginner", "Intermediate", "Advanced"], index=1)
            
            st.write("")
            if st.button("🎯 Generate Pop Quiz"):
                quiz = generate_quiz_mcqs(num_questions=quiz_qty, difficulty=quiz_diff, student_type=st.session_state.student_type)
                if quiz:
                    st.session_state.quiz = quiz
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_graded = False
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            quiz = st.session_state.quiz
            graded = st.session_state.quiz_graded
            
            st.markdown('<div class="notebook-paper">', unsafe_allow_html=True)
            st.markdown(f'<div class="notebook-header">📚 POP QUIZ SHEET ({len(quiz)} Questions - Difficulty: {st.session_state.uploaded_file_name_key.split("_")[-2] if "_range_" in st.session_state.uploaded_file_name_key else "Mixed"})</div>', unsafe_allow_html=True)
            
            for idx, q_item in enumerate(quiz):
                st.markdown(f'<div class="question-block"><b>Question {idx+1}:</b> {q_item["question"]}</div>', unsafe_allow_html=True)
                opts = q_item["options"]
                prev_ans = st.session_state.quiz_answers.get(idx, None)
                
                ans = st.radio(
                    label=f"Radio Option Q{idx+1}",
                    options=opts,
                    index=None if prev_ans is None else opts.index(prev_ans),
                    key=f"mcq_{idx}",
                    disabled=graded,
                    label_visibility="collapsed"
                )
                if ans is not None:
                    st.session_state.quiz_answers[idx] = ans
                    
                if graded:
                    correct_answer = opts[q_item["correct_index"]]
                    if ans == correct_answer:
                        st.markdown(f'<div class="correction-success">✅ <b>Correct!</b> {q_item["explanation"]}</div>', unsafe_allow_html=True)
                    else:
                        chosen_str = ans if ans else "Unanswered"
                        st.markdown(f'<div class="correction-wrong">❌ <b>Wrong.</b> You marked: "{chosen_str}". Correct Answer: "{correct_answer}".<br><i>Explanation: {q_item["explanation"]}</i></div>', unsafe_allow_html=True)
                    st.write("")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if not graded:
                if st.button("📝 Turn In Test Paper"):
                    if len(st.session_state.quiz_answers) < len(quiz):
                        st.warning(f"⚠️ Mr. AI: No blank spaces! Please answer all {len(quiz)} questions before handing in the exam sheet.")
                    else:
                        st.session_state.quiz_graded = True
                        st.rerun()
            else:
                correct_count = sum([1 for idx, q_item in enumerate(quiz) if st.session_state.quiz_answers.get(idx, None) == q_item["options"][q_item["correct_index"]]])
                wrong_count = len(quiz) - correct_count
                total_marks = len(quiz) * 10
                marks = correct_count * 10
                pct = int((correct_count / len(quiz)) * 100)
                
                # Grade logic
                if pct == 100: grade, stamp_color, remark = "A+", "#2e7d32", "🌟 A+! Exceptionally brilliant! Go stand in front of the class for a gold star!"
                elif pct >= 80: grade, stamp_color, remark = "A", "#1565c0", "🍎 A! Very good job! You clearly read your homework."
                elif pct >= 60: grade, stamp_color, remark = "B", "#f57c00", "📘 B! Passing grade, but you can do better. Revise the pages."
                elif pct >= 40: grade, stamp_color, remark = "C", "#fb8c00", "✏️ C! You need extra study sessions. See me after class."
                else: grade, stamp_color, remark = "F", "#c62828", "🎒 F! Did you even open the book? Detentions for you!"
                
                st.markdown(f"""
                <div class="notebook-paper" style="border: 2px solid #d32f2f; background-color: #fff9f9;">
                    <h3 style="color: #d32f2f; border-bottom: 2px dashed #ffcdd2;">📋 Grading Report Card</h3>
                    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center;">
                        <div style="flex: 1; min-width: 250px;">
                            <p>🎒 <b>Student Performance:</b></p>
                            <ul style="list-style-type: '✏\uFE0F '; padding-left: 20px; line-height: 1.8rem;">
                                <li><b>Correct answers:</b> {correct_count} / {len(quiz)}</li>
                                <li><b>Wrong answers:</b> {wrong_count} / {len(quiz)}</li>
                                <li><b>Total Marks:</b> {marks} / {total_marks} points ({pct}%)</li>
                            </ul>
                            <p style="margin-top: 15px; font-style: italic; color: #7f1d1d; font-size: 1.15rem;">💬 <b>Remarks:</b> "{remark}"</p>
                        </div>
                        <div class="grading-stamp-container" style="flex: 0 0 150px;">
                            <div class="grade-stamp" style="border-color: {stamp_color}; color: {stamp_color};">
                                <span class="stamp-title">Mr. AI</span><span>{grade}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🔄 Try a New Quiz"):
                    st.session_state.quiz = None
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_graded = False
                    st.rerun()