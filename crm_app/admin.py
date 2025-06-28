from django.contrib import admin
from .models import Company, Customer, Interaction

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'updated_at', 'deleted_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'birth_date', 'company', 'sales_rep', 'is_active', 'created_at', 'updated_at', 'deleted_at']
    list_filter = ['is_active', 'company', 'sales_rep', 'created_at']
    search_fields = ['first_name', 'last_name', 'company__name']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Nombre Completo'


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'interaction_type', 'interaction_date', 'is_active', 'created_at', 'updated_at', 'deleted_at']
    list_filter = ['interaction_type', 'is_active', 'interaction_date']
    search_fields = ['customer__first_name', 'customer__last_name']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    date_hierarchy = 'interaction_date'
