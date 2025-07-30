from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain.chains import RetrievalQA
from langchain_core.runnables import RunnableMap
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import get_buffer_string
from langchain.memory import ConversationBufferMemory
from langchain.memory import ConversationSummaryMemory
from app.src.utils import getEnvVariable
from typing import List, Optional
from langchain.schema import Document

def generate_answer(retriever, question, is_memory: bool, model_name: Optional[str]=None) -> str:
    """
    Generate an answer to the question using the provided retriever and a language model.
    """
    if is_memory:
        # Prompt template including chat history for conversational memory
        prompt_template = """
        You are an assistant answering questions based on the provided context. Use the context to provide a concise and accurate answer to the question.
        
        Chat History:
        {chat_history}
        
        Context:
        {context}

        Question:
        {question}

        Answer:
        """
    else:
        # Prompt template for single-turn QA (no memory)
        prompt_template = """
        You are an assistant answering questions based on the provided context. Use the context to provide a concise and accurate answer to the question.

        Context:
        {context}

        Question:
        {question}

        Answer:
        """
        
    # Create a prompt template with the provided template
    prompt = PromptTemplate.from_template(prompt_template)
    
    print("Using model:", model_name if model_name else "default OpenAI model")

    # Define the LLM (Language Model) using environment variable for model name
    if model_name:
        llm = ChatOllama(
            model=model_name,
            base_url="https://ai-api.bravesoft.vn:8080", )
    else:
        llm = ChatOpenAI(model=getEnvVariable("OPENAI_MODEL"))
        
    # If memory is enabled, use ConversationSummaryMemory to summarize chat history
    # Otherwise, create a RetrievalQA chain for single-turn QA
    if is_memory:
        # === memory for context ===
        memory = ConversationSummaryMemory(
            llm=llm,
            return_messages=True
        )
        # === Define the chain using RunnableMap ===
        chain = (
            RunnableMap({
                "context": lambda x: retriever.invoke(x["question"]),
                "question": lambda x: x["question"],
                "chat_history": lambda x: get_buffer_string(memory.chat_memory.messages)
            })
            | prompt
            | llm
            | StrOutputParser()
        )

        # === Manually update memory ===
        memory.chat_memory.add_user_message(question)
        response = chain.invoke({"question": question})
        memory.chat_memory.add_ai_message(response)
        return response  # Return the generated answer
    else:
        # Create the RetrievalQA chain with the prompt for single-turn QA
        rag_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt}
        )

        # Invoke the chain with the user's query
        response = rag_chain.invoke({"query": question})
        # Return the generated answer (expects a dict with "result" key)
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

    # Prompt template for answering based on provided context
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
    # Create runnable chain (prompt -> llm)
    chain = prompt | llm

    # Invoke the chain with the context and question
    result = chain.invoke({"context": context, "question": question})
    # Return the generated answer (expects .content attribute)
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
    # Prompt template for generating a follow-up question if needed
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
    followup = result.content.strip()  # Get the follow-up question or "None"

    # Return None if no follow-up is needed, otherwise return the follow-up question
    return None if followup.lower() == "none" else followup