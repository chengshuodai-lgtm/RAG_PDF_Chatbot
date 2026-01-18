from config.settings import DEEPSEEK_API_KEY

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser

from langchain_openai import ChatOpenAI

from utils.logger import logger


def get_prompt():
  logger.debug("Creating chat prompt template.")
  return ChatPromptTemplate.from_messages([
    ("system", "Answer as detailed as possible using the context below. If unknown, say 'I don't know.'"),
    ("human", "Context:\n{context}\n\n\nQuestion:\n{input}")
  ])

def get_llm(model_provider: str, model: str):
  logger.debug(f"Initializing LLM for {model_provider} - {model}")
  if model_provider == "deepseek":
    return ChatOpenAI(
      model=model,
      api_key=DEEPSEEK_API_KEY,
      base_url="https://api.deepseek.com",
      temperature=0.7
    )
  else:
    logger.error(f"Unsupported LLM Provider: {model_provider}")
    raise ValueError(f"Unsupported LLM Provider: {model_provider}")

def format_docs(docs):
  """Format retrieved documents into a single string."""
  return "\n\n".join(doc.page_content for doc in docs)

def build_llm_chain(model_provider: str, model: str, vectorstore):
  logger.debug(f"Building LLM chain for provider: {model_provider}, model: {model}")
  prompt = get_prompt()
  llm = get_llm(model_provider, model)
  retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

  # Build RAG chain using LCEL with correct structure
  rag_chain = (
    RunnableParallel(
      {
        "context": lambda x: format_docs(retriever.invoke(x["input"])),
        "input": lambda x: x["input"]
      }
    )
    | prompt
    | llm
    | StrOutputParser()
  )
  
  # Wrap to maintain compatibility with existing API
  class CompatibleChain:
    def __init__(self, chain):
      self.chain = chain
    
    def invoke(self, input_dict):
      result = self.chain.invoke(input_dict)
      return {"answer": result}
  
  return CompatibleChain(rag_chain)