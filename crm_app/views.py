from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Max, F, CharField, Value
from django.db.models.functions import Concat
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Customer, Company, Interaction
from datetime import datetime


class DashboardView(TemplateView):
    """Vista principal del dashboard con estadísticas generales"""
    template_name = 'crm_app/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        context['stats'] = {
            'total_customers': Customer.objects.count(),
            'total_companies': Company.objects.count(),
            'total_interactions': Interaction.objects.count(),
            'total_sales_reps': User.objects.filter(is_superuser=False).count(),
        }
        
        # Clientes recientes con última interacción
        context['recent_customers'] = Customer.objects.select_related(
            'company', 'sales_rep'
        ).annotate(
            last_interaction_date=Max('interactions__interaction_date'),
            last_interaction_type=Max('interactions__interaction_type')
        ).order_by('-created_at')[:10]
        
        # Estadísticas por sales rep
        sales_rep_stats = Customer.objects.values(
            'sales_rep__first_name', 'sales_rep__last_name'
        ).annotate(
            customer_count=Count('id'),
            sales_rep__get_full_name=Concat(
                'sales_rep__first_name', 
                Value(' '), 
                'sales_rep__last_name',
                output_field=CharField()
            )
        ).order_by('-customer_count')
        
        total_customers = context['stats']['total_customers']
        if total_customers > 0:
            for stat in sales_rep_stats:
                stat['percentage'] = (stat['customer_count'] / total_customers) * 100
        
        context['sales_rep_stats'] = sales_rep_stats
        
        # Estadísticas de tipos de interacción
        interaction_type_stats = Interaction.objects.values('interaction_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        total_interactions = context['stats']['total_interactions']
        if total_interactions > 0:
            for stat in interaction_type_stats:
                stat['percentage'] = (stat['count'] / total_interactions) * 100
        
        context['interaction_type_stats'] = interaction_type_stats
        
        return context


class CustomerListView(ListView):
    """Vista de lista de clientes con filtros y búsqueda"""
    model = Customer
    template_name = 'crm_app/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Customer.objects.select_related(
            'company', 'sales_rep'
        ).annotate(
            last_interaction_date=Max('interactions__interaction_date'),
            last_interaction_type=Max('interactions__interaction_type')
        )
        
        # Filtro de búsqueda por nombre
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search)
            )
        
        # Filtro por empresa
        company_id = self.request.GET.get('company')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Filtro por estado
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Ordenamiento
        ordering = self.request.GET.get('ordering', 'first_name')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['companies'] = Company.objects.filter(is_active=True).order_by('name')
        return context


class CustomerDetailView(DetailView):
    """Vista de detalle de un cliente específico"""
    model = Customer
    template_name = 'crm_app/customer_detail.html'
    context_object_name = 'customer'
    
    def get_queryset(self):
        return Customer.objects.select_related('company', 'sales_rep')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.object
        
        # Estadísticas de interacciones del cliente
        interactions = customer.interactions.all()
        context['interaction_stats'] = {
            'total_count': interactions.count(),
            'call_count': interactions.filter(interaction_type='Call').count(),
            'email_count': interactions.filter(interaction_type='Email').count(),
            'meeting_count': interactions.filter(interaction_type='Meeting').count(),
            'sms_count': interactions.filter(interaction_type='SMS').count(),
            'other_count': interactions.exclude(
                interaction_type__in=['Call', 'Email', 'Meeting', 'SMS']
            ).count(),
        }
        
        # Interacciones recientes (últimas 10)
        context['recent_interactions'] = interactions.order_by('-interaction_date')[:10]
        
        return context


class CompanyListView(ListView):
    """Vista de lista de empresas con estadísticas de clientes"""
    model = Company
    template_name = 'crm_app/company_list.html'
    context_object_name = 'companies'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Company.objects.annotate(
            customer_count=Count('customers')
        )
        
        # Filtro de búsqueda por nombre
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Filtro por estado
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Ordenamiento
        ordering = self.request.GET.get('ordering', 'name')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset


def index(request):
    """Vista temporal para verificar que la aplicación funciona"""
    return HttpResponse("¡CRM App funcionando correctamente! 🚀")
