from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    """Vista temporal para verificar que la aplicación funciona"""
    return HttpResponse("¡CRM App funcionando correctamente! 🚀")
