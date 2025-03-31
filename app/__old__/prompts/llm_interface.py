# app/llm_interface.py

import requests

def build_prompt(chunks, user_question):
    """
    Crée un prompt complet en injectant les documents contextuels.
    """
    context = "\n\n---\n\n".join([chunk for chunk in chunks])

    prompt = f"""
        Tu es un expert de League of Legends.
        
        Voici des extraits du patch note et des changements récents concernant des champions et objets :
        
        {context}
        
        En te basant uniquement sur ce contexte, réponds à la question suivante de manière claire, structurée, et concise :
        
        {user_question}
        
        Si tu n’as pas assez d’informations, indique-le clairement.
    """
    return prompt.strip()

def ask_llm_local(prompt, model="mistral"):
    """
    Appelle un modèle LLM local via Ollama.
    """
    url = "http://localhost:11434/api/generate"

    response = requests.post(url, json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })

    return response.json()["response"].strip()
