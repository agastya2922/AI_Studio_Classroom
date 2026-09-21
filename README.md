# Mr. AI's Studio Classroom 👨‍🏫🍎

An interactive, responsive Streamlit application designed around a vintage, cozy **"Stationary School Teacher"** aesthetic. Students can submit their reading textbooks (PDF, DOCX, TXT), study key concepts, ask questions, and take MCQ pop quizzes graded by their virtual school teacher, **Mr. AI**!

---

## 🌟 Key Features

1. **Stationary School Teacher Aesthetic**:
   - **Wood-Framed Chalkboards**: Custom titles and instructions styled with chalk fonts.
   - **Lined Notebook Paper**: Content sheets complete with margins, lines, and handwritten-styled lettering.
   - **Red Ink Stamps**: Pop quiz reports are graded with red ink circular grade stamps (with customized grades from `A+` through `F` depending on performance).
   - **Interactive Chalkboards and Speech Bubbles**: Chat messages styled to look like student/teacher classroom dialogue.

2. **Strict Textbook Q&A (RAG)**:
   - Mr. AI is highly strict and will only answer concepts found directly in the current lesson pages. If the answers are not there, he will politely instruct the student to open their book and study harder.

3. **Academic MCQ Pop Quizzes**:
   - Automatically generates a 5-question pop quiz based on randomly sampled sections of the book.
   - Restricts questions exclusively to the textbook content.
   - Features real-time grading, counting correct and wrong answers, assigning points, and delivering personalized remarks from the teacher.
   - Includes full explanations for each question upon grading.

4. **Zero-History & Memory Efficient Architecture**:
   - **Ephemeral In-Memory Database**: Replaces file-based vector databases with `chromadb.EphemeralClient`. No database directories are saved to disk, preventing file clutter and resolving Windows file-locking issues.
   - **Textbook Swap Reset**: When a new textbook or chapter range is selected, all past data, memory states, quizzes, and chat histories are wiped clean.
   - **Lesson Slice Slider**: For large books (such as 100+ page PDFs), the student can select a slice range of pages to read (e.g. Pages 1-10). Only these pages are embedded, resulting in faster load times and minimized API credits usage.

---

## 🛠️ Tech Stack

- **Frontend/UI**: [Streamlit](https://streamlit.io/) with custom HTML/CSS injections.
- **RAG & Chat Orchestration**: [LangChain](https://www.langchain.com/) core, community, and splitters.
- **LLM & Embeddings Provider**: [Mistral AI API](https://mistral.ai/) (`ChatMistralAI` with `mistral-small-2506` and `MistralAIEmbeddings`).
- **Vector Database**: [ChromaDB](https://www.trychroma.com/) (Standard client operating in **in-memory Ephemeral mode**).
- **Document Parsers**: [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) for high-speed PDF loading, `python-docx` for Word documents.

---

## 🚀 Getting Started

### 1. Installation

Ensure you have Python 3.9+ installed. Install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a file named `.env` in the root of the directory and insert your Mistral API credential:

```properties
MISTRAL_API_KEY=your_mistral_api_key_goes_here
```

### 3. Run the App

Launch the Streamlit app:

```bash
streamlit run app.py
```

Open `http://localhost:8501` to enter Mr. AI's classroom!

---

## 📂 Project Structure

- `app.py`: The main Streamlit application, containing the UI stylesheet, parser helpers, and the state-management logic.
- `main.py`: Legacy CLI implementation of the RAG bot.
- `test_app_logic.py`: Verification script designed to test RAG pipelines and JSON quiz compilation.
- `Document_loaders/`: Subdirectory containing sample course books for testing.

---

### *🎒 "No talking, keep your eyes on your own paper, and let's get studying!"*