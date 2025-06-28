"""
Comando para limpiar todos los datos ficticios del CRM.

Elimina de forma segura:
- Todas las interacciones
- Todos los clientes  
- Todas las empresas
- Todos los usuarios (excepto superusuarios)

Uso:
    python manage.py clear_data
    python manage.py clear_data --force  # Sin confirmación
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from crm_app.models import Company, Customer, Interaction

class Command(BaseCommand):
    help = 'Limpia todos los datos ficticios del sistema CRM'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la eliminación sin confirmación',
        )

    def handle(self, *args, **options):
        """Método principal del comando"""
        
        self.stdout.write(
            self.style.WARNING('🧹 LIMPIEZA DE DATOS FICTICIOS CRM')
        )
        
        # Mostrar estadísticas actuales
        self._show_current_stats()
        
        # Confirmación (a menos que se use --force)
        if not options['force']:
            confirm = input('\n¿Está seguro que desea eliminar todos los datos? (sí/no): ')
            if confirm.lower() not in ['sí', 'si', 's', 'yes', 'y']:
                self.stdout.write(self.style.ERROR('❌ Operación cancelada'))
                return
        
        try:
            # Realizar limpieza
            self._clear_all_data()
            
            self.stdout.write(
                self.style.SUCCESS('✅ LIMPIEZA COMPLETADA EXITOSAMENTE')
            )
            
        except Exception as e:
            raise CommandError(f'Error durante la limpieza: {str(e)}')

    def _show_current_stats(self):
        """Muestra estadísticas actuales de la base de datos"""
        
        interactions_count = Interaction.objects.count()
        customers_count = Customer.objects.count()
        companies_count = Company.objects.count()
        users_count = User.objects.filter(is_superuser=False).count()
        superusers_count = User.objects.filter(is_superuser=True).count()
        
        self.stdout.write('\n📊 ESTADO ACTUAL DE LA BASE DE DATOS:')
        self.stdout.write(f'  💬 Interacciones: {interactions_count:,}')
        self.stdout.write(f'  👤 Clientes: {customers_count:,}')
        self.stdout.write(f'  🏢 Empresas: {companies_count:,}')
        self.stdout.write(f'  👥 Sales Reps: {users_count}')
        self.stdout.write(f'  🔑 Superusuarios: {superusers_count} (se conservarán)')
        
        total_records = interactions_count + customers_count + companies_count + users_count
        self.stdout.write(f'\n📋 TOTAL A ELIMINAR: {total_records:,} registros')

    def _clear_all_data(self):
        """Elimina todos los datos en el orden correcto"""
        
        self.stdout.write('\n🗑️  Iniciando eliminación...')
        
        with transaction.atomic():
            # 1. Eliminar interacciones (no tienen dependencias)
            interactions_count = Interaction.objects.count()
            if interactions_count > 0:
                Interaction.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Eliminadas {interactions_count:,} interacciones')
                )
            
            # 2. Eliminar clientes (dependen de Company y User)
            customers_count = Customer.objects.count()
            if customers_count > 0:
                Customer.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Eliminados {customers_count:,} clientes')
                )
            
            # 3. Eliminar empresas (pueden tener clientes como dependencia)
            companies_count = Company.objects.count()
            if companies_count > 0:
                Company.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Eliminadas {companies_count:,} empresas')
                )
            
            # 4. Eliminar usuarios (excepto superusuarios)
            users_count = User.objects.filter(is_superuser=False).count()
            if users_count > 0:
                deleted_users = []
                for user in User.objects.filter(is_superuser=False):
                    deleted_users.append(f"{user.get_full_name()} ({user.username})")
                    user.delete()
                
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Eliminados {users_count} usuarios sales reps:')
                )
                for user_info in deleted_users:
                    self.stdout.write(f'    - {user_info}')
        
        # Verificar que la limpieza fue exitosa
        self._verify_cleanup()

    def _verify_cleanup(self):
        """Verifica que la limpieza fue exitosa"""
        
        self.stdout.write('\n🔍 Verificando limpieza...')
        
        interactions_remaining = Interaction.objects.count()
        customers_remaining = Customer.objects.count()
        companies_remaining = Company.objects.count()
        users_remaining = User.objects.filter(is_superuser=False).count()
        superusers_remaining = User.objects.filter(is_superuser=True).count()
        
        # Mostrar estadísticas finales
        self.stdout.write('\n📊 ESTADO FINAL:')
        self.stdout.write(f'  💬 Interacciones: {interactions_remaining}')
        self.stdout.write(f'  👤 Clientes: {customers_remaining}')
        self.stdout.write(f'  🏢 Empresas: {companies_remaining}')
        self.stdout.write(f'  👥 Sales Reps: {users_remaining}')
        self.stdout.write(f'  🔑 Superusuarios: {superusers_remaining} (conservados)')
        
        # Verificar que todo se eliminó correctamente
        total_remaining = interactions_remaining + customers_remaining + companies_remaining + users_remaining
        
        if total_remaining == 0:
            self.stdout.write(
                self.style.SUCCESS('\n🎉 Limpieza perfecta: 0 registros ficticios restantes')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'\n⚠️  Quedan {total_remaining} registros sin eliminar')
            )
            
            # Mostrar detalles de lo que no se pudo eliminar
            if interactions_remaining > 0:
                self.stdout.write(f'  ❗ {interactions_remaining} interacciones no eliminadas')
            if customers_remaining > 0:
                self.stdout.write(f'  ❗ {customers_remaining} clientes no eliminados')
            if companies_remaining > 0:
                self.stdout.write(f'  ❗ {companies_remaining} empresas no eliminadas')
            if users_remaining > 0:
                self.stdout.write(f'  ❗ {users_remaining} usuarios no eliminados')
