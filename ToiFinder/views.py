import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse
from django.views import View

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