import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse
from django.views import View

import chromadb
from sentence_transformers import SentenceTransformer
from django.conf import settings
from ToiFinder.models import Bathroom

from .models import User, Location, Bathroom, Review

# Create your views here.
class UserView(View):
    @method_decorator(csrf_exempt, name='dispatch')
    def get(self, request):
        usuarios = User.objects.all().values()
        return JsonResponse(list(usuarios), safe=False)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = User.objects.create(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            return JsonResponse({
                "message": "Usuario creado correctamente",
                "status": "success",
                "user_id": user.id
            })
        except:
            return HttpResponseBadRequest({"error":"Nel carnal, no se pudo crear el usuario"})

class PaginaView(View):
    def get(self, request):
        baños = Bathroom.objects.all().values()
        return render(request, 'ToiFinder/index.html', {'baños': baños})


@csrf_exempt
def chat_query(request):
    if request.method == 'POST':
        query = request.POST.get('query', '')

        # Carga ChromaDB y modelo
        client = chromadb.PersistentClient(path=str(settings.CHROMA_DB_PATH))
        collection = client.get_collection(name="bathrooms")
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        # Embed la query y busca top 3 resultados
        query_embedding = model.encode(query)
        results = collection.query(query_embeddings=[query_embedding], n_results=3)

        # Formatea respuesta
        response = "\n"
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            bath_id = metadata['bathroom_id']
            bath = Bathroom.objects.get(id=bath_id)
            response += f"Baño recomendado: {metadata['location']} - {doc}\n"

        return JsonResponse({'response': response})
    elif request.method == 'GET':
        # Renderiza la template del chat
        return render(request, 'ToiFinder/chat.html')

    return JsonResponse({'error': 'Método no permitido'}, status=405)