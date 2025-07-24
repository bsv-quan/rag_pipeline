from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from app.src.utils import getEnvVariable
from typing import List, Optional
from langchain.schema import Document

def generate_answer(retriever, question):
    """
    Generate an answer to the question using the provided retriever and a language model.
    """
    prompt_template = """
    You are an assistant answering questions based on the provided context. Use the context to provide a concise and accurate answer to the question.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
    prompt = PromptTemplate.from_template(prompt_template)

    # Define the LLM (Language Model)
    llm = ChatOpenAI(model=getEnvVariable("OPENAI_MODEL"))

    # Create the RetrievalQA chain with the prompt
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt}
    )

    # Invoke the chain with the user's query
    response = rag_chain.invoke({"query": question})
    
    # Return the generated answer
    return response["result"]

def generate_answer_from_docs(question: str, docs: List[Document]) -> str:
    """
    Generate an answer from a list of retrieved documents.

    Args:
        question (str): The user's question.
        docs (List[Document]): List of retrieved documents.

    Returns:
        str: The generated answer.
    """
    # Combine the content of all documents into a single context string
    context = "\n".join([doc.page_content for doc in docs])

    prompt_template = """
    You are an assistant answering questions based on the provided context.
    Use only the context to answer the question as accurately and concisely as possible.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
    prompt = PromptTemplate.from_template(prompt_template)

    # Define the LLM
    llm = ChatOpenAI(model=getEnvVariable("OPENAI_MODEL"))
    # Create runnable chain
    chain = prompt | llm

    # Invoke the chain with the context and question
    result = chain.invoke({"context": context, "question": question})
    # Return the generated answer
    return result.content

def generate_followup_question_if_needed(question: str, answer: str) -> Optional[str]:
    """
    Generate a follow-up question if the current answer is insufficient.

    Args:
        question (str): The original user question.
        answer (str): The current answer.

    Returns:
        Optional[str]: The follow-up question if needed, otherwise None.
    """
    prompt_template = """
    Given the original question and the current answer, decide whether a follow-up question is needed
    to clarify or improve the answer.

    If the answer is sufficient, respond with only "None".
    Otherwise, generate a follow-up question that helps improve or complete the answer.

    Original Question: {question}
    Current Answer: {answer}

    Follow-up Question:
    """

    prompt = PromptTemplate.from_template(prompt_template)
    # Define the LLM
    llm = ChatOpenAI(model=getEnvVariable("OPENAI_MODEL"))
    # Create the LLM chain with the prompt
    chain = prompt | llm

    # Invoke the chain with the question and answer
    result = chain.invoke({"question": question, "answer": answer})
    followup = result.content.strip()

    # Return None if no follow-up is needed, otherwise return the follow-up question
    return None if followup.lower() == "none" else followup