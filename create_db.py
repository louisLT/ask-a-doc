import os
import logging

import pinecone
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter

log = logging.getLogger(__name__)

logging.basicConfig(
    format="%(levelname)s : %(message)s", level=logging.INFO, force=True
)

NAMESPACE = "model-series"
TEST_QUERY = "what is the inspection time interval ?"
FILE = os.environ["INPUT_FILE_ADDR"]
INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]

# initialize pinecone
pinecone.init(
    api_key=os.environ["PINECONE_API_KEY"],
    environment=os.environ["PINECONE_ENV"]
)

# split documents
# by default, text splitter works page per page (separator "\n\n"),
# you can use another separator as argument
text_splitter = CharacterTextSplitter(chunk_size=1000,
                                      chunk_overlap=100)
loader = PyPDFLoader(FILE)
documents = loader.load_and_split(text_splitter=text_splitter)

# Select embeddings
embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])

# create db
db = Pinecone.from_documents(documents,
                             embeddings,
                             index_name=INDEX_NAME,
                             namespace=NAMESPACE)

# Create retriever interface
retriever = db.as_retriever()
qa = RetrievalQA.from_chain_type(llm=OpenAI(openai_api_key=os.environ["OPENAI_API_KEY"]),
                                 chain_type='stuff',
                                 retriever=retriever,
                                 return_source_documents=True)

# test retriever
result_ = qa(TEST_QUERY)
best_scores = db.similarity_search_with_score(TEST_QUERY,
                                              k=2,
                                              namespace=NAMESPACE)

# useful snippets

# index_description = pinecone.describe_index(index_name)
# index = pinecone.Index(index_name)
# index_stats_response = index.describe_index_stats()

# delete
# index = pinecone.Index(index_name)
# delete_response = index.delete(namespace=NAMESPACE, delete_all=True)
