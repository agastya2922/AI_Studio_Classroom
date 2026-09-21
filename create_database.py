import importlib
import builtins

try:
  PyMuPDFLoader = importlib.import_module(
    "langchain_community.document_loaders"
  ).PyMuPDFLoader
except builtins.ImportError as error:
  raise builtins.ImportError(
    "Install langchain-community with "
    "'python -m pip install -U langchain-community'."
  ) from error
try:
  RecursiveCharacterTextSplitter = importlib.import_module(
    "langchain_text_splitters"
  ).RecursiveCharacterTextSplitter
except builtins.ImportError:
  try:
    RecursiveCharacterTextSplitter = importlib.import_module(
      "langchain.text_splitter"
    ).RecursiveCharacterTextSplitter
  except builtins.ImportError as error:
    raise builtins.ImportError(
      "Install langchain-text-splitters with "
      "'python -m pip install -U langchain-text-splitters'."
    ) from error
try:
  MistralAIEmbeddings = importlib.import_module(
    "langchain_mistralai"
  ).MistralAIEmbeddings
except builtins.ImportError as error:
  raise builtins.ImportError(
    "Install the MistralAI LangChain integration with "
    "'python -m pip install -U langchain-mistralai'."
  ) from error
try:
  Chroma = importlib.import_module(
    "langchain_community.vectorstores"
  ).Chroma
except builtins.ImportError as error:
  raise builtins.ImportError(
    "Install langchain-community with "
    "'python -m pip install -U langchain-community'."
  ) from error
try:
  load_dotenv = importlib.import_module("dotenv").load_dotenv
except builtins.ImportError as error:
  raise builtins.ImportError(
    "Install python-dotenv with 'python -m pip install -U python-dotenv'."
  ) from error

load_dotenv()

loader = PyMuPDFLoader("Document_loaders/Deeplearning.pdf")
docs = loader.load()

splitter =RecursiveCharacterTextSplitter(
  chunk_size =1000,
  chunk_overlap=200
)
chunks = splitter.split_documents(docs)
embedding_model = MistralAIEmbeddings()

vectorstore = Chroma.from_documents(
  documents = chunks,
  embedding =embedding_model,
  persist_directory="Chroma_db"
)