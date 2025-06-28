"""
Comando para validar la integridad de los datos del CRM.

Verifica:
- Conteos de registros
- Integridad referencial
- Distribución de datos
- Consistencia temporal
- Estadísticas de uso

Uso:
    python manage.py validate_data
    python manage.py validate_data --detailed  # Reporte detallado
    python manage.py validate_data --performance  # Test de rendimiento
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.models import Count, Q, Min, Max, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from crm_app.models import Company, Customer, Interaction

class Command(BaseCommand):
    help = 'Valida la integridad y consistencia de los datos del CRM'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Muestra un reporte detallado con estadísticas avanzadas',
        )
        parser.add_argument(
            '--performance',
            action='store_true',
            help='Ejecuta tests de rendimiento en consultas típicas',
        )

    def handle(self, *args, **options):
        """Método principal del comando"""
        
        self.stdout.write(
            self.style.SUCCESS('🔍 VALIDACIÓN DE INTEGRIDAD DE DATOS CRM')
        )
        
        try:
            # Validaciones básicas
            self._basic_validation()
            
            # Validaciones de integridad referencial
            self._referential_integrity()
            
            # Validaciones de negocio
            self._business_logic_validation()
            
            # Reporte detallado si se solicita
            if options['detailed']:
                self._detailed_statistics()
            
            # Test de rendimiento si se solicita
            if options['performance']:
                self._performance_tests()
            
            self.stdout.write(
                self.style.SUCCESS('\n✅ VALIDACIÓN COMPLETADA')
            )
            
        except Exception as e:
            raise CommandError(f'Error durante la validación: {str(e)}')

    def _basic_validation(self):
        """Validaciones básicas de conteo"""
        
        self.stdout.write('\n📊 VALIDACIÓN BÁSICA DE CONTEOS:')
        
        # Obtener conteos
        users_count = User.objects.filter(is_superuser=False).count()
        companies_count = Company.objects.count()
        customers_count = Customer.objects.count()
        interactions_count = Interaction.objects.count()
        superusers_count = User.objects.filter(is_superuser=True).count()
        
        # Mostrar conteos actuales
        self.stdout.write(f'  👥 Sales Representatives: {users_count}')
        self.stdout.write(f'  🏢 Empresas: {companies_count}')
        self.stdout.write(f'  👤 Clientes: {customers_count}')
        self.stdout.write(f'  💬 Interacciones: {interactions_count:,}')
        self.stdout.write(f'  🔑 Superusuarios: {superusers_count}')
        
        # Validar rangos esperados
        issues = []
        
        if users_count < 3:
            issues.append(f'Pocos sales reps: {users_count} (esperado: 3)')
        
        if companies_count < 30:
            issues.append(f'Pocas empresas: {companies_count} (esperado: ~50)')
        
        if customers_count < 800:
            issues.append(f'Pocos clientes: {customers_count} (esperado: ~1000)')
        
        if interactions_count < 40000:  # Mínimo esperado para mode rápido
            issues.append(f'Pocas interacciones: {interactions_count:,} (esperado: >40K)')
        
        if issues:
            self.stdout.write(self.style.WARNING('\n⚠️  PROBLEMAS ENCONTRADOS:'))
            for issue in issues:
                self.stdout.write(f'  ❗ {issue}')
        else:
            self.stdout.write(self.style.SUCCESS('  ✅ Conteos están en rangos esperados'))

    def _referential_integrity(self):
        """Valida integridad referencial"""
        
        self.stdout.write('\n🔗 VALIDACIÓN DE INTEGRIDAD REFERENCIAL:')
        
        # Clientes huérfanos (sin empresa o sales rep)
        orphan_customers_company = Customer.objects.filter(company__isnull=True).count()
        orphan_customers_rep = Customer.objects.filter(sales_rep__isnull=True).count()
        
        # Interacciones huérfanas (sin cliente)
        orphan_interactions = Interaction.objects.filter(customer__isnull=True).count()
        
        # Clientes con empresas inexistentes
        invalid_company_refs = Customer.objects.exclude(
            company__in=Company.objects.all()
        ).count()
        
        # Clientes con sales reps inexistentes
        invalid_rep_refs = Customer.objects.exclude(
            sales_rep__in=User.objects.all()
        ).count()
        
        # Mostrar resultados
        integrity_issues = []
        
        if orphan_customers_company > 0:
            integrity_issues.append(f'Clientes sin empresa: {orphan_customers_company}')
        
        if orphan_customers_rep > 0:
            integrity_issues.append(f'Clientes sin sales rep: {orphan_customers_rep}')
        
        if orphan_interactions > 0:
            integrity_issues.append(f'Interacciones sin cliente: {orphan_interactions}')
        
        if invalid_company_refs > 0:
            integrity_issues.append(f'Referencias de empresa inválidas: {invalid_company_refs}')
        
        if invalid_rep_refs > 0:
            integrity_issues.append(f'Referencias de sales rep inválidas: {invalid_rep_refs}')
        
        if integrity_issues:
            self.stdout.write(self.style.ERROR('\n❌ PROBLEMAS DE INTEGRIDAD:'))
            for issue in integrity_issues:
                self.stdout.write(f'  ❗ {issue}')
        else:
            self.stdout.write(self.style.SUCCESS('  ✅ Integridad referencial correcta'))

    def _business_logic_validation(self):
        """Valida lógica de negocio"""
        
        self.stdout.write('\n💼 VALIDACIÓN DE LÓGICA DE NEGOCIO:')
        
        # Fechas de nacimiento futuras
        future_births = Customer.objects.filter(
            birth_date__gt=timezone.now().date()
        ).count()
        
        # Fechas de interacción futuras
        future_interactions = Interaction.objects.filter(
            interaction_date__gt=timezone.now()
        ).count()
        
        # Interacciones antes de la creación del cliente
        invalid_interaction_dates = Interaction.objects.filter(
            interaction_date__lt=F('customer__created_at')
        ).count()
        
        # Clientes menores de edad (menos de 18 años)
        eighteen_years_ago = timezone.now().date() - timedelta(days=18*365)
        underage_customers = Customer.objects.filter(
            birth_date__gt=eighteen_years_ago
        ).count()
        
        # Distribución de clientes por sales rep (verificar balance)
        rep_distribution = Customer.objects.values('sales_rep__username').annotate(
            count=Count('id')
        ).order_by('sales_rep__username')
        
        max_customers = max([rep['count'] for rep in rep_distribution]) if rep_distribution else 0
        min_customers = min([rep['count'] for rep in rep_distribution]) if rep_distribution else 0
        imbalance_ratio = max_customers / min_customers if min_customers > 0 else float('inf')
        
        # Mostrar resultados
        business_issues = []
        
        if future_births > 0:
            business_issues.append(f'Fechas de nacimiento futuras: {future_births}')
        
        if future_interactions > 0:
            business_issues.append(f'Interacciones en el futuro: {future_interactions}')
        
        if invalid_interaction_dates > 0:
            business_issues.append(f'Interacciones antes de creación del cliente: {invalid_interaction_dates}')
        
        if underage_customers > 0:
            business_issues.append(f'Clientes menores de edad: {underage_customers}')
        
        if imbalance_ratio > 2.0:  # Más del 100% de diferencia
            business_issues.append(f'Desbalance en distribución de clientes (ratio: {imbalance_ratio:.1f})')
        
        if business_issues:
            self.stdout.write(self.style.WARNING('\n⚠️  PROBLEMAS DE LÓGICA DE NEGOCIO:'))
            for issue in business_issues:
                self.stdout.write(f'  ❗ {issue}')
        else:
            self.stdout.write(self.style.SUCCESS('  ✅ Lógica de negocio correcta'))
        
        # Mostrar distribución por sales rep
        self.stdout.write('\n👥 DISTRIBUCIÓN POR SALES REP:')
        for rep in rep_distribution:
            self.stdout.write(f'  {rep["sales_rep__username"]}: {rep["count"]} clientes')

    def _detailed_statistics(self):
        """Estadísticas detalladas del sistema"""
        
        self.stdout.write('\n📈 ESTADÍSTICAS DETALLADAS:')
        
        # Estadísticas de empresas
        companies_with_customers = Company.objects.filter(
            customers__isnull=False
        ).distinct().count()
        companies_without_customers = Company.objects.filter(
            customers__isnull=True
        ).count()
        
        self.stdout.write('\n🏢 EMPRESAS:')
        self.stdout.write(f'  Con clientes: {companies_with_customers}')
        self.stdout.write(f'  Sin clientes: {companies_without_customers}')
        
        # Top empresas por número de clientes
        top_companies = Company.objects.annotate(
            customer_count=Count('customers')
        ).order_by('-customer_count')[:5]
        
        self.stdout.write('  Top 5 empresas por clientes:')
        for company in top_companies:
            self.stdout.write(f'    {company.name}: {company.customer_count} clientes')
        
        # Estadísticas de clientes
        customers_with_birth_date = Customer.objects.filter(
            birth_date__isnull=False
        ).count()
        active_customers = Customer.objects.filter(is_active=True).count()
        
        self.stdout.write('\n👤 CLIENTES:')
        self.stdout.write(f'  Con fecha de nacimiento: {customers_with_birth_date}')
        self.stdout.write(f'  Activos: {active_customers}')
        
        # Rango de edades
        if customers_with_birth_date > 0:
            ages = []
            for customer in Customer.objects.filter(birth_date__isnull=False):
                age = (timezone.now().date() - customer.birth_date).days // 365
                ages.append(age)
            
            if ages:
                min_age = min(ages)
                max_age = max(ages)
                avg_age = sum(ages) / len(ages)
                
                self.stdout.write(f'  Edad mínima: {min_age} años')
                self.stdout.write(f'  Edad máxima: {max_age} años')
                self.stdout.write(f'  Edad promedio: {avg_age:.1f} años')
        
        # Estadísticas de interacciones
        interaction_stats = Interaction.objects.values('interaction_type').annotate(
            count=Count('id'),
            percentage=Count('id') * 100.0 / Interaction.objects.count()
        ).order_by('-count')
        
        self.stdout.write('\n💬 INTERACCIONES POR TIPO:')
        for stat in interaction_stats:
            self.stdout.write(
                f'  {stat["interaction_type"]}: {stat["count"]:,} ({stat["percentage"]:.1f}%)'
            )
        
        # Actividad por mes (últimos 6 meses)
        six_months_ago = timezone.now() - timedelta(days=180)
        recent_interactions = Interaction.objects.filter(
            interaction_date__gte=six_months_ago
        ).count()
        
        self.stdout.write(f'\n📅 Interacciones últimos 6 meses: {recent_interactions:,}')
        
        # Clientes más activos
        most_active_customers = Customer.objects.annotate(
            interaction_count=Count('interactions')
        ).order_by('-interaction_count')[:5]
        
        self.stdout.write('\n⭐ TOP 5 CLIENTES MÁS ACTIVOS:')
        for customer in most_active_customers:
            self.stdout.write(
                f'  {customer.get_full_name()} ({customer.company.name}): '
                f'{customer.interaction_count} interacciones'
            )

    def _performance_tests(self):
        """Test básicos de rendimiento"""
        
        self.stdout.write('\n⚡ TESTS DE RENDIMIENTO:')
        
        # Test 1: Lista de clientes con empresa y última interacción
        start_time = datetime.now()
        
        customers_with_data = Customer.objects.select_related(
            'company', 'sales_rep'
        ).prefetch_related('interactions').all()[:100]
        
        # Forzar evaluación de la query
        list(customers_with_data)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write(f'  📋 Lista 100 clientes con relaciones: {duration:.3f}s')
        
        # Test 2: Conteo de interacciones por tipo
        start_time = datetime.now()
        
        interaction_counts = Interaction.objects.values('interaction_type').annotate(
            count=Count('id')
        )
        list(interaction_counts)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write(f'  📊 Agregación por tipo de interacción: {duration:.3f}s')
        
        # Test 3: Búsqueda de cliente por nombre
        start_time = datetime.now()
        
        search_results = Customer.objects.filter(
            Q(first_name__icontains='María') | Q(last_name__icontains='García')
        ).select_related('company', 'sales_rep')[:20]
        list(search_results)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write(f'  🔍 Búsqueda por nombre (20 resultados): {duration:.3f}s')
        
        # Test 4: Estadísticas por sales rep
        start_time = datetime.now()
        
        rep_stats = User.objects.filter(is_superuser=False).annotate(
            customer_count=Count('assigned_customers'),
            interaction_count=Count('assigned_customers__interactions')
        )
        list(rep_stats)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write(f'  👥 Estadísticas por sales rep: {duration:.3f}s')
        
        # Evaluación general de rendimiento
        total_records = (Customer.objects.count() + 
                        Interaction.objects.count() + 
                        Company.objects.count())
        
        self.stdout.write(f'\n📊 Total de registros en sistema: {total_records:,}')
        
        if duration < 1.0:
            self.stdout.write(self.style.SUCCESS('  ✅ Rendimiento excelente'))
        elif duration < 3.0:
            self.stdout.write(self.style.SUCCESS('  ✅ Rendimiento bueno'))
        elif duration < 5.0:
            self.stdout.write(self.style.WARNING('  ⚠️  Rendimiento aceptable'))
        else:
            self.stdout.write(self.style.ERROR('  ❌ Rendimiento deficiente'))
