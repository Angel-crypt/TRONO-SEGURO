import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse
from django.views import View
from django.db.models import Avg, Count
from django.conf import settings

import chromadb
from sentence_transformers import SentenceTransformer
from ToiFinder.models import Bathroom

from .models import User, Location, Bathroom, Review

# Create your views here.

class PaginaView(View):
    def get(self, request):
        baños = Bathroom.objects.all().values()
        return render(request, 'ToiFinder/index.html', {'baños': baños})

class LoginView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        return render(request, 'ToiFinder/login.html')
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = User.objects.get(username=data['username'], password=data['password'])
            return JsonResponse({
                "message": "Login exitoso",
                "status": "success",
                "user_id": user.id
            })
        except User.DoesNotExist:
            return JsonResponse({"error": "Credenciales inválidas"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Formato de datos inválido"}, status=400)
        except KeyError:
            return JsonResponse({"error": "Faltan campos requeridos (username, password)"}, status=400)

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

class CatalogView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        Vista para mostrar el catálogo de baños con información básica
        """
        bathrooms = Bathroom.objects.select_related('location').annotate(
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).all()
        
        # Procesar los datos para el template
        for bathroom in bathrooms:
            # Si no tiene reseñas, asignar rating 0
            if bathroom.average_rating is None:
                bathroom.average_rating = 0
        
        context = {
            'bathrooms': bathrooms,
            'total_bathrooms': bathrooms.count(),
        }
        
        return render(request, 'toifinder/catalog.html', context)