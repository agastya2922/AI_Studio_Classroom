import importlib

try:
    load_dotenv = importlib.import_module("dotenv").load_dotenv
except ImportError:
    def load_dotenv():
        pass
_mistralai = importlib.import_module("langchain_mistralai")
MistralAIEmbeddings = _mistralai.MistralAIEmbeddings
_chroma = importlib.import_module("langchain_chroma")
Chroma = _chroma.Chroma
ChatMistralAI = _mistralai.ChatMistralAI
_prompts = importlib.import_module("langchain_core.prompts")
ChatPromptTemplate = _prompts.ChatPromptTemplate
load_dotenv()


embedding_model = MistralAIEmbeddings()
vectorstore = Chroma(
  persist_directory="Chroma_db",
  embedding_function=embedding_model
)

retriever = vectorstore.as_retriever(
  search_type="mmr",
  search_kwargs={
    "k":4,"fetch_k":10,"lambda_mult":0.5
  }

)
llm = ChatMistralAI(model="mistral-small-2506")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful AI assistant.

Use ONLY the provided context to answer the question.

If the answer is not present in the context,
say: "I could not find the answer in the document."
"""
        ),
        (
            "human",
            """Context:
{context}

Question:
{question}
"""
        )
    ]
)

print("Rag system created ")

print("press 0 to exit ")

while True:
    query = input("You : ")
    if query == "0":
        break 
    
    docs = retriever.invoke(query)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )
    
    final_prompt = prompt.invoke({
        "context" :context,
        "question": query
    })
    
    response = llm.invoke(final_prompt)

    print(f"\n AI: {response.content}")
    