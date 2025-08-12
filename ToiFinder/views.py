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
                Q(location__name__icontains=search_query)
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

    def post(self, request):
        try:
            data = json.loads(request.body)
            name = data.get('name')
            location_name = data.get('location_name')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            is_free = data.get('is_free', True)
            has_accessibility = data.get('has_accessibility', False)
            is_clean = data.get('is_clean', True)

            if not all([name, location_name, latitude, longitude]):
                return JsonResponse({"error": "Faltan campos requeridos"}, status=400)

            # Create Location
            location = Location.objects.create(
                name=location_name,
                latitude=latitude,
                longitude=longitude
            )

            # Create Bathroom
            bathroom = Bathroom.objects.create(
                name=name,
                location=location,
                is_free=is_free,
                has_accessibility=has_accessibility,
                is_clean=is_clean
            )

            return JsonResponse({"message": "Baño agregado exitosamente", "bathroom_id": bathroom.id})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Formato de datos inválido"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Error al agregar el baño: {str(e)}"}, status=500)

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

    def post(self, request, bathroom_id):
        """
        API para agregar una reseña al baño
        """
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            rating = data.get('rating')
            comment = data.get('comment')
            
            if not all([user_id, rating]):
                return JsonResponse({"error": "Faltan campos requeridos (user_id, rating)"}, status=400)
            
            try:
                user = User.objects.get(id=user_id)
                bathroom = Bathroom.objects.get(id=bathroom_id)
            except (User.DoesNotExist, Bathroom.DoesNotExist):
                return JsonResponse({"error": "Usuario o baño no encontrado"}, status=404)
            
            # Verificar si el usuario ya ha dejado una reseña
            if Review.objects.filter(user=user, bathroom=bathroom).exists():
                return JsonResponse({"error": "Ya has dejado una reseña para este baño"}, status=400)
            
            # Crear la reseña
            review = Review.objects.create(
                bathroom=bathroom,
                user=user,
                rating=int(rating),
                comment=comment
            )
            
            return JsonResponse({
                "message": "Reseña agregada exitosamente",
                "review_id": review.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Formato de datos inválido"}, status=400)
        except ValueError:
            return JsonResponse({"error": "Valor de rating inválido"}, status=400)
        except Exception as e:
            print(f"Error al agregar reseña: {str(e)}")
            return JsonResponse({"error": f"Error interno del servidor: {str(e)}"}, status=500)

class ProfileView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """
        Vista para mostrar el perfil del usuario
        """
        return render(request, 'ToiFinder/profile.html')
    
    def post(self, request):
        """
        API para obtener estadísticas del usuario vía AJAX
        """
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            
            if not user_id:
                return JsonResponse({"error": "user_id requerido"}, status=400)
            
            # Verificar que el usuario existe
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({"error": "Usuario no encontrado"}, status=404)
            
            # Obtener estadísticas del usuario
            user_reviews = Review.objects.filter(user_id=user_id)
            
            # Calcular average_rating manualmente para evitar errores
            total_reviews = user_reviews.count()
            avg_rating = 0
            if total_reviews > 0:
                total_rating = sum([review.rating for review in user_reviews])
                avg_rating = total_rating / total_reviews
            
            stats = {
                'username': user.username,
                'email': user.email,
                'member_since': user.created_at.strftime('%d/%m/%Y') if user.created_at else 'N/A',
                'total_reviews': total_reviews,
                'average_rating': round(avg_rating, 1),
                'recent_reviews': []
            }
            
            # Obtener las 5 reseñas más recientes con información del baño
            recent_reviews = user_reviews.select_related('bathroom', 'bathroom__location').order_by('-created_at')[:5]
            
            for review in recent_reviews:
                stats['recent_reviews'].append({
                    'id': review.id,
                    'bathroom_name': review.bathroom.name,
                    'bathroom_location': review.bathroom.location.name,
                    'rating': review.rating,
                    'comment': review.comment or '',
                    'created_at': review.created_at.strftime('%d/%m/%Y'),
                    'bathroom_id': review.bathroom.id
                })
            
            return JsonResponse(stats)
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Formato de datos inválido"}, status=400)
        except Exception as e:
            print(f"Error en ProfileView: {str(e)}")  # Para debug
            return JsonResponse({"error": f"Error interno del servidor: {str(e)}"}, status=500)