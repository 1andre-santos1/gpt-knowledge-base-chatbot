from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
import os
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import yaml

# This function will load config file and return the config object
def load_config(config_file_path="config.yml"):
    data = ''
    with open(config_file_path,"r") as file_object:
        data=yaml.load(file_object,Loader=yaml.SafeLoader)
    return data

# This function processes the PDF file and returns the docsearch and chain
def process_file(file_path):

    print(f'Processing knowledge base: {file_path}') 

    # Set up your vector store
    reader = PdfReader(file_path)

    # Extract text from PDF
    raw_text = ''
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            raw_text += text

    # Split text into chunks
    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=1000,
        chunk_overlap=200,
        length_function = len,
    )

    texts = text_splitter.split_text(raw_text)

    embeddings = OpenAIEmbeddings()

    docsearch = FAISS.from_texts(texts, embeddings)

    chain = load_qa_chain(OpenAI(), chain_type='stuff')

    return docsearch, chain

# This function takes in a question and returns the answer
def answer_question(question, docsearch, chain):
    docs = docsearch.similarity_search(question)
    answer = chain.run(input_documents=docs, question=question)
    return answer

config = load_config()

api_key = config['openai']['api_key']
file_path = config['knowledge_base']['file_path']

# Set up your OpenAI API credentials
os.environ["OPENAI_API_KEY"] = api_key
docsearch, chain = process_file(file_path)

# This function takes in a question and returns the answer in a loop
while True:
    query = input('Enter your question: ')
    answer = answer_question(query, docsearch, chain)
    print(answer)