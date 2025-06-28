from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# ========== CHOICES SIMPLIFICADAS ==========

INTERACTION_TYPE_CHOICES = [
    ('Call', 'Call'),
    ('Email', 'Email'),
    ('SMS', 'SMS'),
    ('Facebook', 'Facebook'),
    ('WhatsApp', 'WhatsApp'),
    ('Meeting', 'Meeting'),
    ('Other', 'Other'),
]

# ========== MODELOS SIMPLIFICADOS ==========

class Company(models.Model):
    """Modelo para empresas - Versión simplificada"""
    
    # Campos requeridos
    name = models.CharField(max_length=200, unique=True, verbose_name="Nombre")
    
    # Campos de control (orden exacto: is_active, created_at, updated_at, deleted_at)
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Eliminación")
    
    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['name']
        db_table = 'crm_app_companies'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('crm_app:company_detail', kwargs={'pk': self.pk})


class Customer(models.Model):
    """Modelo para clientes - Versión simplificada"""
    
    # Campos requeridos
    first_name = models.CharField(max_length=100, verbose_name="Nombre")
    last_name = models.CharField(max_length=100, verbose_name="Apellido")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    
    # Relaciones requeridas
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='customers',
        verbose_name="Empresa"
    )
    sales_rep = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='assigned_customers',
        verbose_name="Representante"
    )
    
    # Campos de control (orden exacto: is_active, created_at, updated_at, deleted_at)
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Eliminación")
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['last_name', 'first_name']
        db_table = 'crm_app_customers'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company.name}"
    
    def get_absolute_url(self):
        return reverse('crm_app:customer_detail', kwargs={'pk': self.pk})
    
    def get_full_name(self):
        """Retorna el nombre completo del cliente"""
        return f"{self.first_name} {self.last_name}"


class Interaction(models.Model):
    """Modelo para interacciones - Versión simplificada"""
    
    # Campos requeridos
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='interactions',
        verbose_name="Cliente Asociado"
    )
    interaction_type = models.CharField(
        max_length=20,
        choices=INTERACTION_TYPE_CHOICES,
        verbose_name="Tipo de Interacción"
    )
    interaction_date = models.DateTimeField(default=timezone.now, verbose_name="Fecha de la Interacción")
    
    # Campos de control (orden exacto: is_active, created_at, updated_at, deleted_at)
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Eliminación")
    
    class Meta:
        verbose_name = "Interacción"
        verbose_name_plural = "Interacciones"
        ordering = ['-interaction_date']
        db_table = 'crm_app_interactions'
    
    def __str__(self):
        return f"{self.interaction_type} - {self.customer.get_full_name()} - {self.interaction_date.strftime('%Y-%m-%d')}"
    
    def get_absolute_url(self):
        return reverse('crm_app:interaction_detail', kwargs={'pk': self.pk})
