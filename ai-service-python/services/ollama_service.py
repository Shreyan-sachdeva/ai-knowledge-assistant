import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(question, relevant_chunks):
    context = "\n\n".join(relevant_chunks)

    prompt = f"""You are an internal assistant.
Give only two to three line answer.
Answer ONLY using the provided context below.
Do NOT use any external or general knowledge, even if you know the answer.
If the answer is not in the context, say:
'I couldn't find the relevant information.'

{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.1
    )

    return response.choices[0].message.content