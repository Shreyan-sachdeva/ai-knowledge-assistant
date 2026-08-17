import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(question, relevant_chunks):
    context = "\n\n".join(relevant_chunks)

    prompt = f"""You are an internal assistant that answers questions using only the provided document context.

Rules:
- Answer in 2-3 lines, in a natural conversational tone.
- Use ONLY the context below. Do NOT use any external or general knowledge, even if you know the answer.
- Do not add preamble like "Based on the context" — answer directly.
- Paraphrase in your own words rather than copying text verbatim.
- If the user sends a greeting or casual message (like "hello", "hi", "bye", "thanks"), respond naturally and briefly without needing the document context.
- If the question is unrelated to the documents and the answer is not in the context, say exactly: "I couldn't find relevant information in the uploaded documents."

Context:
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