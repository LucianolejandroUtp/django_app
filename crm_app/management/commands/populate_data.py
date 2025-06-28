"""
Comando para poblar la base de datos con datos ficticios del CRM.

Genera:
- 3 representantes de ventas
- ~50 empresas
- 1000 clientes
- ~500,000 interacciones

Uso:
    python manage.py populate_data
    python manage.py populate_data --clear  # Limpia datos previos
    python manage.py populate_data --fast   # Modo rápido con menos interacciones
"""

import random
import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction, connection
from django.db.models import F
from django.utils import timezone
from faker import Faker
from crm_app.models import Company, Customer, Interaction

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Pobla la base de datos con datos ficticios para el sistema CRM'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpia todos los datos antes de generar nuevos',
        )
        parser.add_argument(
            '--fast',
            action='store_true',
            help='Modo rápido: genera menos interacciones (50 por cliente)',
        )
        parser.add_argument(
            '--companies',
            type=int,
            default=50,
            help='Número de empresas a generar (default: 50)',
        )
        parser.add_argument(
            '--customers',
            type=int,
            default=1000,
            help='Número de clientes a generar (default: 1000)',
        )

    def handle(self, *args, **options):
        """Método principal del comando"""
        
        self.stdout.write(
            self.style.SUCCESS('🎲 INICIANDO GENERACIÓN DE DATOS FICTICIOS CRM')
        )
        
        # Configurar Faker en español
        self.fake = Faker('es_ES')
        Faker.seed(42)  # Seed fijo para resultados reproducibles
        random.seed(42)
        
        # Configurar parámetros
        self.companies_count = options['companies']
        self.customers_count = options['customers']
        self.interactions_per_customer = 50 if options['fast'] else 500
        self.clear_data = options['clear']
        
        try:
            # Limpiar datos si se solicita
            if self.clear_data:
                self._clear_existing_data()
            
            # Generar datos
            self._create_sales_representatives()
            self._create_companies()
            self._create_customers()
            self._create_interactions()
            
            # Validar resultados
            self._validate_data()
            
            self.stdout.write(
                self.style.SUCCESS('✅ GENERACIÓN COMPLETADA EXITOSAMENTE')
            )
            
        except Exception as e:
            logger.error(f"Error durante la generación: {str(e)}")
            raise CommandError(f'Error en la generación de datos: {str(e)}')

    def _clear_existing_data(self):
        """Limpia datos existentes de forma segura"""
        
        self.stdout.write('🧹 Limpiando datos existentes...')
        
        with transaction.atomic():
            # Eliminar en orden correcto (por dependencias)
            interactions_count = Interaction.objects.count()
            customers_count = Customer.objects.count()
            companies_count = Company.objects.count()
            users_count = User.objects.filter(is_superuser=False).count()
            
            if interactions_count > 0:
                Interaction.objects.all().delete()
                self.stdout.write(f'  ❌ Eliminadas {interactions_count} interacciones')
            
            if customers_count > 0:
                Customer.objects.all().delete()
                self.stdout.write(f'  ❌ Eliminados {customers_count} clientes')
            
            if companies_count > 0:
                Company.objects.all().delete()
                self.stdout.write(f'  ❌ Eliminadas {companies_count} empresas')
            
            if users_count > 0:
                User.objects.filter(is_superuser=False).delete()
                self.stdout.write(f'  ❌ Eliminados {users_count} usuarios (sales reps)')
        
        self.stdout.write(self.style.SUCCESS('✅ Limpieza completada'))

    def _create_sales_representatives(self):
        """Crea 3 representantes de ventas"""
        
        self.stdout.write('👥 Creando representantes de ventas...')
        
        sales_reps_data = [
            {
                'username': 'maria_garcia',
                'first_name': 'María',
                'last_name': 'García',
                'email': 'maria.garcia@company.com',
                'password': 'demo123456'
            },
            {
                'username': 'carlos_rodriguez',
                'first_name': 'Carlos',
                'last_name': 'Rodríguez',
                'email': 'carlos.rodriguez@company.com',
                'password': 'demo123456'
            },
            {
                'username': 'ana_martinez',
                'first_name': 'Ana',
                'last_name': 'Martínez',
                'email': 'ana.martinez@company.com',
                'password': 'demo123456'
            }
        ]
        
        created_users = []
        
        with transaction.atomic():
            for rep_data in sales_reps_data:
                # Verificar si ya existe
                if not User.objects.filter(username=rep_data['username']).exists():
                    user = User.objects.create_user(
                        username=rep_data['username'],
                        first_name=rep_data['first_name'],
                        last_name=rep_data['last_name'],
                        email=rep_data['email'],
                        password=rep_data['password'],
                        is_staff=False,
                        is_active=True
                    )
                    created_users.append(user)
                    self.stdout.write(f'  ✅ Creado: {user.get_full_name()} ({user.username})')
        
        self.sales_reps = User.objects.filter(is_superuser=False)
        self.stdout.write(
            self.style.SUCCESS(f'✅ {self.sales_reps.count()} representantes de ventas listos')
        )

    def _create_companies(self):
        """Crea empresas con datos realistas"""
        
        self.stdout.write(f'🏢 Creando {self.companies_count} empresas...')
        
        # Sectores empresariales variados
        sectors = [
            'Tecnología', 'Manufactura', 'Servicios', 'Retail', 'Construcción',
            'Alimentaria', 'Farmacéutica', 'Automotive', 'Energía', 'Logística',
            'Financiera', 'Inmobiliaria', 'Telecomunicaciones', 'Turismo', 'Educación'
        ]
        
        companies_to_create = []
        used_names = set()
        
        # Generar nombres únicos
        while len(companies_to_create) < self.companies_count:
            company_name = self.fake.company()
            
            # Agregar variaciones para hacerlos más únicos
            if random.choice([True, False]):
                suffix = random.choice(['S.A.', 'S.L.', 'Group', 'Corp', 'Solutions', 'Systems'])
                company_name = f"{company_name} {suffix}"
            
            # Verificar unicidad
            if company_name not in used_names and len(company_name) <= 200:
                used_names.add(company_name)
                companies_to_create.append(
                    Company(
                        name=company_name,
                        is_active=True
                    )
                )
        
        # Inserción masiva
        with transaction.atomic():
            Company.objects.bulk_create(companies_to_create, batch_size=100)
        
        self.companies = list(Company.objects.all())
        self.stdout.write(
            self.style.SUCCESS(f'✅ {len(self.companies)} empresas creadas')
        )

    def _create_customers(self):
        """Crea clientes distribuidos entre empresas y sales reps"""
        
        self.stdout.write(f'👤 Creando {self.customers_count} clientes...')
        
        customers_to_create = []
        sales_reps_list = list(self.sales_reps)
        
        # Distribuir clientes equitativamente entre sales reps
        customers_per_rep = self.customers_count // len(sales_reps_list)
        
        # Fecha base: hace 2 años para dar tiempo a las interacciones
        base_date = timezone.now() - timedelta(days=730)
        
        for i in range(self.customers_count):
            # Asignar sales rep de forma balanceada
            sales_rep = sales_reps_list[i % len(sales_reps_list)]
            
            # Seleccionar empresa aleatoria
            company = random.choice(self.companies)
            
            # Generar fecha de nacimiento realista (18-65 años)
            birth_date = None
            if random.random() > 0.1:  # 90% tienen fecha de nacimiento
                age_years = random.randint(18, 65)
                birth_date = (timezone.now().date() - timedelta(days=age_years * 365))
            
            # Fecha de creación del cliente: distribución en los últimos 2 años
            days_ago = random.randint(1, 730)  # Entre 1 día y 2 años atrás
            customer_created_at = base_date + timedelta(days=days_ago)
            
            customer = Customer(
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                birth_date=birth_date,
                company=company,
                sales_rep=sales_rep,
                is_active=random.choice([True, True, True, False])  # 75% activos
            )
            
            # Establecer fecha de creación manualmente
            customer.created_at = customer_created_at
            customer.updated_at = customer_created_at
            
            customers_to_create.append(customer)
            
            # Mostrar progreso cada 100 clientes
            if (i + 1) % 100 == 0:
                self.stdout.write(f'  📝 Preparados {i + 1}/{self.customers_count} clientes...')
        
        # Crear clientes individualmente para controlar created_at
        self.stdout.write('  🕐 Creando clientes con fechas históricas...')
        created_customers = []
        
        with transaction.atomic():
            for i, customer_data in enumerate(customers_to_create):
                # Crear cliente individual
                customer = Customer.objects.create(
                    first_name=customer_data.first_name,
                    last_name=customer_data.last_name,
                    birth_date=customer_data.birth_date,
                    company=customer_data.company,
                    sales_rep=customer_data.sales_rep,
                    is_active=customer_data.is_active
                )
                
                # Actualizar fecha de creación después de la creación
                Customer.objects.filter(id=customer.id).update(
                    created_at=customer_data.created_at,
                    updated_at=customer_data.created_at
                )
                
                created_customers.append(customer)
                
                # Mostrar progreso cada 100 clientes
                if (i + 1) % 100 == 0:
                    self.stdout.write(f'  💾 Creados {i + 1}/{len(customers_to_create)} clientes')
        
        self.customers = Customer.objects.all().order_by('created_at')
        self.stdout.write(
            self.style.SUCCESS(f'✅ {self.customers.count()} clientes creados con fechas históricas')
        )

    def _create_interactions(self):
        """Crea interacciones masivas de forma optimizada"""
        
        total_interactions = self.customers_count * self.interactions_per_customer
        self.stdout.write(f'💬 Creando ~{total_interactions:,} interacciones...')
        
        # Tipos de interacción con probabilidades realistas
        interaction_types = [
            ('Call', 0.40),      # 40%
            ('Email', 0.30),     # 30%
            ('Meeting', 0.15),   # 15%
            ('SMS', 0.08),       # 8%
            ('WhatsApp', 0.05),  # 5%
            ('Facebook', 0.02),  # 2%
        ]
        
        # Preparar lista ponderada de tipos
        weighted_types = []
        for interaction_type, weight in interaction_types:
            weighted_types.extend([interaction_type] * int(weight * 100))
        
        interactions_to_create = []
        batch_size = 1000
        created_count = 0
        
        for customer in self.customers:
            # Número aleatorio de interacciones por cliente (±20% del objetivo)
            num_interactions = random.randint(
                int(self.interactions_per_customer * 0.8),
                int(self.interactions_per_customer * 1.2)
            )
            
            # Rango de fechas válido: desde creación del cliente hasta hace 1 hora MÍNIMO
            start_date = customer.created_at
            now = timezone.now()
            end_date = now - timedelta(hours=1)  # Margen de seguridad de 1 hora
            
            # Si el cliente es muy nuevo (creado hace menos de 1 hora), ajustar rango
            if start_date >= end_date:
                # Para clientes muy nuevos, usar un rango de 30 días en el pasado
                end_date = start_date + timedelta(days=30)
                # Asegurar que end_date no sea futuro
                if end_date > now - timedelta(hours=1):
                    end_date = now - timedelta(hours=1)
                    # Si aún hay problema, mover start_date más atrás
                    if start_date >= end_date:
                        start_date = end_date - timedelta(days=7)
            
            for _ in range(num_interactions):
                # Generar fecha simple: días aleatorios entre start y end
                days_diff = max(1, (end_date - start_date).days)
                
                random_days = random.randint(0, days_diff)
                random_hours = random.randint(0, 23)
                random_minutes = random.randint(0, 59)
                
                interaction_date = start_date + timedelta(
                    days=random_days,
                    hours=random_hours,
                    minutes=random_minutes
                )
                
                # VERIFICACIÓN CRÍTICA: asegurar que no sea futuro ni anterior al cliente
                max_allowed_date = now - timedelta(hours=1)
                
                if interaction_date >= max_allowed_date:
                    # Si es futuro, moverlo a un momento seguro en el pasado
                    days_back = random.randint(1, 30)
                    hours_back = random.randint(1, 23)
                    interaction_date = max_allowed_date - timedelta(
                        days=days_back, 
                        hours=hours_back
                    )
                
                if interaction_date < customer.created_at:
                    # Si es anterior al cliente, moverlo después de la creación
                    interaction_date = customer.created_at + timedelta(
                        hours=random.randint(1, 72)  # Entre 1 y 72 horas después
                    )
                    # Verificar nuevamente que no sea futuro
                    if interaction_date >= max_allowed_date:
                        interaction_date = max_allowed_date - timedelta(hours=random.randint(1, 24))
                
                # Tipo de interacción ponderado
                interaction_type = random.choice(weighted_types)
                
                interactions_to_create.append(
                    Interaction(
                        customer=customer,
                        interaction_type=interaction_type,
                        interaction_date=interaction_date,
                        is_active=random.choice([True, True, True, False])  # 75% activas
                    )
                )
                
                # Insertar por lotes para optimizar memoria
                if len(interactions_to_create) >= batch_size:
                    with transaction.atomic():
                        Interaction.objects.bulk_create(interactions_to_create, batch_size=batch_size)
                    
                    created_count += len(interactions_to_create)
                    interactions_to_create = []
                    
                    self.stdout.write(f'  💾 Insertadas {created_count:,}/{total_interactions:,} interacciones')
        
        # Insertar lote final
        if interactions_to_create:
            with transaction.atomic():
                Interaction.objects.bulk_create(interactions_to_create, batch_size=batch_size)
            created_count += len(interactions_to_create)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {created_count:,} interacciones creadas')
        )
        
        # POST-PROCESAMIENTO: Corregir automáticamente cualquier fecha problemática
        self._fix_problematic_interactions()

    def _fix_problematic_interactions(self):
        """Corrige automáticamente todas las interacciones con fechas problemáticas"""
        
        self.stdout.write('🔧 Post-procesamiento: verificando fechas de interacciones...')
        
        # Encontrar interacciones problemáticas (anteriores a creación del cliente)
        problematic_interactions = Interaction.objects.filter(
            interaction_date__lt=F('customer__created_at')
        ).select_related('customer')
        
        problematic_count = problematic_interactions.count()
        
        if problematic_count == 0:
            self.stdout.write('  ✅ Todas las fechas son correctas')
            return
        
        self.stdout.write(f'  🔧 Corrigiendo {problematic_count} interacciones problemáticas...')
        
        # Corregir cada interacción problemática con una lógica más simple y robusta
        fixed_count = 0
        now = timezone.now()
        
        for interaction in problematic_interactions:
            customer_creation_date = interaction.customer.created_at
            
            # Lógica de corrección simplificada:
            # Añadir un delta de tiempo aleatorio a la fecha de creación del cliente.
            # Esto asegura que la interacción SIEMPRE es posterior.
            time_since_creation = now - customer_creation_date
            
            # Asegurarse de que hay un intervalo de tiempo para generar una fecha
            if time_since_creation.total_seconds() > 60: # Más de 1 minuto
                random_offset_seconds = random.uniform(60, time_since_creation.total_seconds())
                new_date = customer_creation_date + timedelta(seconds=random_offset_seconds)
            else:
                # Si el cliente fue creado hace menos de un minuto, simplemente añade un pequeño delta
                new_date = customer_creation_date + timedelta(seconds=random.randint(1, 59))

            # Doble verificación para asegurar que no sea futura
            if new_date > now:
                new_date = now

            interaction.interaction_date = new_date
            interaction.save(update_fields=['interaction_date'])
            fixed_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'  ✅ Corregidas {fixed_count} interacciones problemáticas')
        )
        
        # Verificación final
        remaining_problematic = Interaction.objects.filter(
            interaction_date__lt=F('customer__created_at')
        ).count()
        
        if remaining_problematic == 0:
            self.stdout.write('  🎉 Todas las fechas están ahora correctas')
        else:
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  Aún quedan {remaining_problematic} fechas problemáticas')
            )

    def _validate_data(self):
        """Valida la integridad de los datos generados"""
        
        self.stdout.write('🔍 Validando integridad de datos...')
        
        # Conteos
        users_count = User.objects.filter(is_superuser=False).count()
        companies_count = Company.objects.count()
        customers_count = Customer.objects.count()
        interactions_count = Interaction.objects.count()
        
        # Mostrar estadísticas
        self.stdout.write(f'  📊 Usuarios (sales reps): {users_count}')
        self.stdout.write(f'  📊 Empresas: {companies_count}')
        self.stdout.write(f'  📊 Clientes: {customers_count}')
        self.stdout.write(f'  📊 Interacciones: {interactions_count:,}')
        
        # Validaciones de integridad
        orphan_customers = Customer.objects.filter(company__isnull=True).count()
        orphan_interactions = Interaction.objects.filter(customer__isnull=True).count()
        
        if orphan_customers > 0:
            self.stdout.write(
                self.style.WARNING(f'⚠️  {orphan_customers} clientes sin empresa')
            )
        
        if orphan_interactions > 0:
            self.stdout.write(
                self.style.WARNING(f'⚠️  {orphan_interactions} interacciones sin cliente')
            )
        
        # Distribución por sales rep
        self.sales_reps = User.objects.filter(is_superuser=False)
        for sales_rep in self.sales_reps:
            rep_customers = Customer.objects.filter(sales_rep=sales_rep).count()
            self.stdout.write(
                f'  👤 {sales_rep.get_full_name()}: {rep_customers} clientes'
            )
        
        # Distribución por tipo de interacción
        from django.db.models import Count
        interaction_stats = Interaction.objects.values('interaction_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        self.stdout.write('  📊 Distribución de interacciones:')
        for stat in interaction_stats:
            percentage = (stat['count'] / interactions_count) * 100
            self.stdout.write(
                f'    {stat["interaction_type"]}: {stat["count"]:,} ({percentage:.1f}%)'
            )
        
        self.stdout.write(self.style.SUCCESS('✅ Validación completada'))
