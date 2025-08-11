import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest, JsonResponse
from django.views import View
from django.db.models import Avg, Count, Q
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

import chromadb
from sentence_transformers import SentenceTransformer
from ToiFinder.models import Bathroom

from .models import User, Location, Bathroom, Review

# Create your views here.

class PaginaView(View):
    def get(self, request):
        bathrooms = Bathroom.objects.all().select_related('location')
        return render(request, 'ToiFinder/index.html', {'bathrooms': bathrooms})

class LoginView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        return render(request, 'ToiFinder/login.html')
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return JsonResponse(
                    {"error": "Faltan campos requeridos (username, password)"}, 
                    status=400
                )
            
            user = User.objects.get(username=username, password=password)
            return JsonResponse({
                "message": "Login exitoso",
                "status": "success",
                "user_id": user.id
            })
        except User.DoesNotExist:
            return JsonResponse({"error": "Credenciales inválidas"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Formato de datos inválido"}, status=400)
        except Exception as e:
            return JsonResponse({"error": "Error interno del servidor"}, status=500)

@csrf_exempt
def chat_query(request):
    if request.method == 'POST':
        try:
            query = request.POST.get('query', '').strip()
            
            if not query:
                return JsonResponse({'error': 'Query vacía'}, status=400)

            # Carga ChromaDB y modelo
            client = chromadb.PersistentClient(path=str(settings.CHROMA_DB_PATH))
            collection = client.get_collection(name="bathrooms")
            model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

            # Embed la query y busca top 3 resultados
            query_embedding = model.encode(query)
            results = collection.query(query_embeddings=[query_embedding], n_results=3)

            # Formatea respuesta
            response_text = ""
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
                bathroom_id = metadata.get('bathroom_id')
                if bathroom_id:
                    try:
                        bathroom = Bathroom.objects.select_related('location').get(id=bathroom_id)
                        response_text += f"{i}. {bathroom.name} - {metadata.get('location', 'Ubicación no disponible')}\n"
                        response_text += f"   Descripción: {doc[:100]}...\n\n"
                    except Bathroom.DoesNotExist:
                        continue

            if not response_text:
                response_text = "No se encontraron baños que coincidan con tu búsqueda."

            return JsonResponse({'response': response_text})
            
        except Exception as e:
            return JsonResponse({'error': 'Error procesando la consulta'}, status=500)
    
    elif request.method == 'GET':
        return render(request, 'ToiFinder/chat.html')

    return JsonResponse({'error': 'Método no permitido'}, status=405)

class CatalogView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
   
    def get(self, request):
        # Obtener parámetros de filtrado
        search_query = request.GET.get('q', '').strip()
        rating_filter = request.GET.get('rating', '')
        order_by = request.GET.get('order_by', '')
        is_free = request.GET.get('free') == 'on'
        is_accessible = request.GET.get('accessible') == 'on'
        is_clean = request.GET.get('clean') == 'on'

        # Base queryset optimizado con select_related y prefetch_related
        bathrooms = Bathroom.objects.select_related('location').prefetch_related('reviews').annotate(
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )

        # Contador total antes de filtros
        total_bathrooms = bathrooms.count()

        # --- Aplicar filtros ---
        has_filters = False

        # Búsqueda por nombre o ubicación
        if search_query:
            bathrooms = bathrooms.filter(
                Q(name__icontains=search_query) | 
                Q(location__name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            has_filters = True

        # Filtro por rating mínimo
        if rating_filter and rating_filter.isdigit():
            rating_min = float(rating_filter)
            bathrooms = bathrooms.filter(
                average_rating__gte=rating_min
            ).exclude(average_rating__isnull=True)
            has_filters = True

        # Filtros por características
        if is_free:
            bathrooms = bathrooms.filter(is_free=True)
            has_filters = True
            
        if is_accessible:
            bathrooms = bathrooms.filter(has_accessibility=True)
            has_filters = True
            
        if is_clean:
            bathrooms = bathrooms.filter(is_clean=True)
            has_filters = True

        # --- Ordenamiento ---
        if order_by == 'rating_asc':
            bathrooms = bathrooms.order_by('average_rating')
        elif order_by == 'rating_desc':
            bathrooms = bathrooms.order_by('-average_rating')
        elif order_by == 'reviews_asc':
            bathrooms = bathrooms.order_by('review_count')
        elif order_by == 'reviews_desc':
            bathrooms = bathrooms.order_by('-review_count')
        else:
            # Ordenamiento por defecto: mejor rating primero, luego por número de reseñas
            bathrooms = bathrooms.order_by('-average_rating', '-review_count')

        # Contador después de filtros
        results_count = bathrooms.count()

        # --- Paginación ---
        paginator = Paginator(bathrooms, 12)  # 12 baños por página
        page_number = request.GET.get('page', 1)
        
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        # Construir query string para paginación
        filter_params = []
        if search_query:
            filter_params.append(f'q={search_query}')
        if rating_filter:
            filter_params.append(f'rating={rating_filter}')
        if order_by:
            filter_params.append(f'order_by={order_by}')
        if is_free:
            filter_params.append('free=on')
        if is_accessible:
            filter_params.append('accessible=on')
        if is_clean:
            filter_params.append('clean=on')
            
        filter_query_string = '&'.join(filter_params)

        context = {
            'bathrooms': page_obj,
            'page_obj': page_obj,
            'has_filters': has_filters,
            'results_count': results_count,
            'total_bathrooms': total_bathrooms,
            'filter_query_string': filter_query_string,
            # Mantener valores de filtros para el formulario
            'current_search': search_query,
            'current_rating': rating_filter,
            'current_free': is_free,
            'current_accessible': is_accessible,
            'current_clean': is_clean,
        }

        return render(request, 'toifinder/catalog.html', context)

class DetailView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, bathroom_id):
        """
        Vista para mostrar los detalles de un baño específico
        """
        bathroom = get_object_or_404(
            Bathroom.objects.select_related('location')
                            .prefetch_related('reviews__user')
                            .annotate(
                                average_rating=Avg('reviews__rating'),
                                review_count=Count('reviews')
                            ),
            id=bathroom_id
        )

        # Obtener reseñas recientes
        recent_reviews = bathroom.reviews.select_related('user').order_by('-created_at')[:5]

        context = {
            'bathroom': bathroom,
            'recent_reviews': recent_reviews,
        }

        return render(request, 'toifinder/detail.html', context)