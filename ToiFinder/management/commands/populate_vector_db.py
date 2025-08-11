# python manage.py populate_vector_db
from django.core.management.base import BaseCommand
from ToiFinder.models import Bathroom, Location, Review
import chromadb
from sentence_transformers import SentenceTransformer
from django.conf import settings

class Command(BaseCommand):
    help = 'Pobla la base de datos vectorial con datos de baños'

    def handle(self, *args, **kwargs):
        # Cliente ChromaDB persistente
        client = chromadb.PersistentClient(path=str(settings.CHROMA_DB_PATH))
        collection = client.get_or_create_collection(name="bathrooms")

        # Modelo de embeddings
        model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

        # Genera documentos
        documents = []
        metadatas = []
        ids = []
        for bath in Bathroom.objects.all():
            loc = bath.location
            accessibility = 'accesible para discapacitados' if bath.has_accessibility else 'no accesible para discapacitados'
            free = 'gratuito' if bath.is_free else 'de pago'
            clean = 'limpio' if bath.is_clean else 'no limpio'
            reviews_str = ' '.join([rev.comment for rev in Review.objects.filter(bathroom=bath) if rev.comment]) or 'Sin reseñas.'

            doc = f"Baño: {bath.name} en {loc.name} (lat: {loc.latitude}, lon: {loc.longitude}). Es {accessibility}, {free} y {clean}. Reseñas: {reviews_str}"
            documents.append(doc)
            metadatas.append({"bathroom_id": bath.id, "location": loc.name})  # Metadata para recuperación
            ids.append(str(bath.id))

        # Agrega a la colección (embeddings automáticos)
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
        self.stdout.write(self.style.SUCCESS('Base vectorial poblada exitosamente!'))