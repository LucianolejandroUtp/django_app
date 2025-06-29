from django.urls import path
from . import views

app_name = 'crm_app'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Clientes
    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    
    # Empresas
    path('companies/', views.CompanyListView.as_view(), name='company_list'),
    
    # Vista temporal (mantener por compatibilidad)
    path('test/', views.index, name='index'),
]
