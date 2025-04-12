from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import os

# Adjusting Python path to include backend retrieval module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.backend.retrieve import generate_answer  # Your RAG pipeline

@csrf_exempt
def ask_question(request):
    """
    Django view to handle user questions via POST request.
    Integrates conversational history and invokes the RAG pipeline.
    """
    if request.method == "POST":
        try:
            try:
                data = json.loads(request.body.decode("utf-8"))
            except UnicodeDecodeError:
                data = json.loads(request.body.decode("latin-1"))

            question = data.get("question", "")
            messages = data.get("messages", [])

            if not question:
                return JsonResponse({"error": "No question provided."}, status=400)

            # Building prompt with conversation history
            context_prompt = ""
            for msg in messages:
                if msg["role"] == "user":
                    context_prompt += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    context_prompt += f"Assistant: {msg['content']}\n"

            context_prompt += f"User: {question}\nAssistant:"

            # Generate response using RAG pipeline
            response = generate_answer(context_prompt)

            return JsonResponse({"answer": response})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON request."}, status=400)
