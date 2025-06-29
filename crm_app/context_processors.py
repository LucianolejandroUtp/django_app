from .models import Customer, Company, Interaction
from django.contrib.auth.models import User


def crm_context(request):
    """Context processor para datos globales del CRM"""
    
    # Solo calcular si el usuario está autenticado
    if not request.user.is_authenticated:
        return {}
    
    try:
        return {
            'customers_count': Customer.objects.count(),
            'companies_count': Company.objects.count(),
            'interactions_count': Interaction.objects.count(),
            'sales_reps_count': User.objects.filter(is_superuser=False).count(),
        }
    except Exception:
        # En caso de error (ej: migraciones no aplicadas), retornar valores por defecto
        return {
            'customers_count': 0,
            'companies_count': 0,
            'interactions_count': 0,
            'sales_reps_count': 0,
        }
