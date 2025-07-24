from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from app.src.utils import getEnvVariable

def generate_answer(retriever, question):
    prompt_template = """
    You are an assistant answering questions based on the provided context. Use the context to provide a concise and accurate answer to the question.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
    prompt = PromptTemplate.from_template(prompt_template)

    # 2. Define the LLM
    llm = ChatOpenAI(model=getEnvVariable("OPENAI_MODEL"))

    # 3. Create the RAG chain with your prompt
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt}
    )

    # 4. Invoke the chain with your query
    response = rag_chain.invoke({"query": question})
    
    # 5. Return the result
    return response["result"]