from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.backend.retrieve import generate_answer  # Ton pipeline RAG

@csrf_exempt
def ask_question(request):
    if request.method == "POST":
        try:
            try:
                data = json.loads(request.body.decode("utf-8"))
            except UnicodeDecodeError:
                data = json.loads(request.body.decode("latin-1"))

            question = data.get("question", "")
            messages = data.get("messages", [])

            if not question:
                return JsonResponse({"error": "Aucune question fournie."}, status=400)

            # Construction du prompt avec l'historique
            context_prompt = ""
            for msg in messages:
                if msg["role"] == "user":
                    context_prompt += f"Utilisateur : {msg['content']}\n"
                elif msg["role"] == "assistant":
                    context_prompt += f"Assistant : {msg['content']}\n"

            context_prompt += f"Utilisateur : {question}\nAssistant :"

            response = generate_answer(context_prompt)

            return JsonResponse({"answer": response})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Requête JSON invalide."}, status=400)
