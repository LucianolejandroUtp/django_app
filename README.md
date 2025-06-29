# 🚀 Django CRM System

![Django](https://img.shields.io/badge/Django-5.2.3-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12.9-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-4.6-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

Sistema de gestión de relaciones con clientes (CRM) desarrollado en Django con interfaz moderna usando el template Atlantis-Lite. Diseñado para manejar grandes volúmenes de datos (500K+ interacciones) con rendimiento optimizado.

## 📋 Tabla de Contenidos

- [🛠️ Tecnologías](#%EF%B8%8F-tecnologías)
- [📦 Instalación](#-instalación)
- [🚀 Ejecución](#-ejecución)
- [📊 Población de Datos](#-población-de-datos)
- [🌐 Acceso al Sistema](#-acceso-al-sistema)
- [🏗️ Arquitectura](#%EF%B8%8F-arquitectura)
- [✅ Funcionalidades Implementadas](#-funcionalidades-implementadas)
- [📱 Capturas de Pantalla](#-capturas-de-pantalla)
- [🔧 Comandos Útiles](#-comandos-útiles)
- [📚 Documentación Adicional](#-documentación-adicional)

## 🛠️ Tecnologías

### **Backend**
- **Python** `3.12.9` - Lenguaje de programación principal
- **Django** `5.2.3` - Framework web principal
- **SQLite** - Base de datos por defecto (desarrollo)

### **Frontend**
- **Atlantis-Lite** - Template Bootstrap 4 Admin Dashboard
- **Bootstrap** `4.6` - Framework CSS para diseño responsive
- **Font Awesome** `5.x` - Iconografía
- **jQuery** `3.2.1` - Manipulación DOM y AJAX

### **Herramientas de Desarrollo**
- **Faker** `37.4.0` - Generación de datos ficticios
- **Virtual Environment** - Aislamiento de dependencias
- **Django Admin** - Panel de administración

### **Versiones Específicas**
```
asgiref==3.8.1
Django==5.2.3
Faker==37.4.0
pip==25.1.1
sqlparse==0.5.3
tzdata==2025.2
```

## 📦 Instalación

### **Prerrequisitos**
- Python 3.12.9 o superior
- Git
- PowerShell (Windows) o Terminal (Linux/Mac)

### **1. Clonar el Repositorio**
```bash
git clone https://github.com/LucianolejandroUtp/django_app.git
cd django_app
```

### **2. Crear y Activar Entorno Virtual**

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### **3. Instalar Dependencias**
```bash
pip install -r requirements.txt
```

Si no existe `requirements.txt`, instalar manualmente:
```bash
pip install Django==5.2.3
pip install Faker==37.4.0
```

### **4. Configurar Base de Datos**
```bash
python manage.py makemigrations
python manage.py migrate
```

### **5. Crear Superusuario (Opcional)**
```bash
python manage.py createsuperuser
```

## 🚀 Ejecución

### **Activar Entorno Virtual** (siempre necesario)
```powershell
# Windows
D:/develop/django_app/venv/Scripts/Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### **Iniciar Servidor de Desarrollo**
```bash
python manage.py runserver
```

El servidor estará disponible en: **http://127.0.0.1:8000/**

## 📊 Población de Datos

El sistema incluye comandos personalizados para generar datos ficticios realistas:

### **Generar Dataset Completo**
```bash
python manage.py populate_data
```

**Esto genera:**
- 3 representantes de ventas
- 50 empresas
- 1,000 clientes
- ~500,000 interacciones

### **Opciones Avanzadas**

**Modo rápido** (menos interacciones):
```bash
python manage.py populate_data --fast
```

**Limpiar datos previos:**
```bash
python manage.py populate_data --clear
```

**Personalizar cantidades:**
```bash
python manage.py populate_data --companies 30 --customers 500
```

### **Validar Datos**
```bash
python manage.py validate_data --summary
```

### **Limpiar Datos**
```bash
python manage.py clear_data
```

## 🌐 Acceso al Sistema

### **Vista Principal del CRM**
- **URL:** http://127.0.0.1:8000/
- **Descripción:** Dashboard con estadísticas generales y métricas del sistema

### **Lista de Clientes** (Funcionalidad Principal)
- **URL:** http://127.0.0.1:8000/customers/
- **Funcionalidades:**
  - Búsqueda por nombre
  - Filtros: empresa, cumpleaños, estado
  - Ordenamiento: nombre, empresa, cumpleaños, última interacción
  - Paginación (25 clientes por página)
  - Botón de reseteo de filtros

### **Lista de Empresas**
- **URL:** http://127.0.0.1:8000/companies/
- **Funcionalidades:**
  - Lista todas las empresas con conteo de clientes
  - Búsqueda y filtros básicos

### **Detalle de Cliente**
- **URL:** http://127.0.0.1:8000/customers/{id}/
- **Funcionalidades:**
  - Información completa del cliente
  - Historial de interacciones
  - Estadísticas personalizadas

### **Panel de Administración**
- **URL:** http://127.0.0.1:8000/admin/
- **Acceso:** Superusuario o desde menú de usuario
- **Funcionalidades:** Gestión completa de datos

## 🏗️ Arquitectura

### **Estructura del Proyecto**
```
django_app/
├── manage.py                   # Utilidad CLI de Django
├── db.sqlite3                  # Base de datos SQLite
├── django_app/                 # Configuración del proyecto
│   ├── settings.py            # Configuración principal
│   ├── urls.py                # URLs principales
│   └── wsgi.py                # Punto de entrada WSGI
├── crm_app/                    # Aplicación CRM principal
│   ├── models.py              # Modelos de datos
│   ├── views.py               # Lógica de vistas
│   ├── urls.py                # URLs de la aplicación
│   ├── admin.py               # Configuración de admin
│   ├── templates/             # Plantillas HTML
│   │   ├── base.html          # Plantilla base
│   │   └── crm_app/           # Plantillas específicas
│   ├── static/crm_app/        # Archivos estáticos
│   └── management/commands/   # Comandos personalizados
│       ├── populate_data.py   # Generación de datos
│       ├── clear_data.py      # Limpieza de datos
│       └── validate_data.py   # Validación de integridad
├── docs/                       # Documentación
│   ├── Atlantis-Lite/         # Template UI (solo consulta)
│   └── *.md                   # Documentación técnica
└── venv/                      # Entorno virtual
```

### **Modelos de Datos**

#### **Company** (Empresas)
```python
- name: CharField(200, unique=True)
- is_active: BooleanField(default=True)
- created_at, updated_at: DateTimeField
```

#### **Customer** (Clientes)
```python
- first_name, last_name: CharField(100)
- birth_date: DateField(null=True, blank=True)
- company: ForeignKey(Company)
- sales_rep: ForeignKey(User)
- is_active: BooleanField(default=True)
- created_at, updated_at: DateTimeField
```

#### **Interaction** (Interacciones)
```python
- customer: ForeignKey(Customer)
- interaction_type: CharField(choices)
- interaction_date: DateTimeField
- is_active: BooleanField(default=True)
- created_at, updated_at: DateTimeField
```

### **Tipos de Interacción**
- Call (Llamada)
- Email (Correo)
- SMS (Mensaje de texto)
- Facebook (Red social)
- WhatsApp (Mensajería)
- Meeting (Reunión)
- Other (Otros)

### **Optimizaciones de Rendimiento**
- **select_related()** para relaciones ForeignKey
- **prefetch_related()** para relaciones inversas
- **Annotations** para campos calculados
- **Subqueries** para última interacción
- **F() expressions** con nulls_last para ordenamiento
- **bulk_create()** para inserción masiva
- **Índices** en campos de búsqueda frecuente

## ✅ Funcionalidades Implementadas

### **✅ Dashboard Principal**
- [x] Estadísticas generales del sistema
- [x] Conteos de clientes, empresas, interacciones
- [x] Clientes recientes con última interacción
- [x] Distribución por representantes de ventas
- [x] Estadísticas por tipo de interacción
- [x] Interfaz responsive con Atlantis-Lite

### **✅ Sistema de Clientes**
- [x] Lista completa de clientes paginada
- [x] Búsqueda por nombre (case-insensitive)
- [x] Filtros avanzados:
  - [x] Por empresa
  - [x] Por estado (activo/inactivo)
  - [x] Por cumpleaños (hoy, esta semana, este mes, próximo mes)
- [x] Ordenamiento completo:
  - [x] Por nombre (A-Z, Z-A)
  - [x] Por empresa (A-Z, Z-A)
  - [x] Por cumpleaños (jóvenes/mayores)
  - [x] Por última interacción (reciente/antigua)
- [x] Botón de reseteo de filtros
- [x] Vista de detalle individual
- [x] Información de representante asignado
- [x] Cálculo automático de edad
- [x] Historial de interacciones

### **✅ Sistema de Empresas**
- [x] Lista de empresas con conteo de clientes
- [x] Búsqueda por nombre
- [x] Filtros por estado
- [x] Ordenamiento por nombre y cantidad de clientes

### **✅ Sistema de Interacciones**
- [x] Registro masivo de interacciones
- [x] Diferentes tipos de comunicación
- [x] Timestamp automático
- [x] Vinculación con clientes
- [x] Estadísticas por tipo
- [x] Historial ordenado por fecha

### **✅ Interfaz de Usuario**
- [x] Template Atlantis-Lite Bootstrap 4
- [x] Diseño responsive y moderno
- [x] Sidebar simplificado con navegación
- [x] Breadcrumbs en páginas
- [x] Iconografía Font Awesome
- [x] Tablas con estilos profesionales
- [x] Formularios de filtrado intuitivos
- [x] Badges con contadores dinámicos
- [x] Paginación estilizada
- [x] Mensajes flash para feedback

### **✅ Administración**
- [x] Panel de Django Admin configurado
- [x] ModelAdmin personalizado para todos los modelos
- [x] Filtros y búsquedas en admin
- [x] Campos de solo lectura para timestamps
- [x] Acceso desde menú de usuario

### **✅ Comandos de Gestión**
- [x] `populate_data` - Generación de datos ficticios
- [x] `clear_data` - Limpieza de datos
- [x] `validate_data` - Validación de integridad
- [x] Opciones avanzadas y modo rápido
- [x] Progreso detallado con logging
- [x] Manejo de errores y transacciones

### **✅ Rendimiento y Optimización**
- [x] Consultas optimizadas con select_related
- [x] Annotations para campos calculados
- [x] Manejo eficiente de 500K+ registros
- [x] Tiempo de carga < 3 segundos
- [x] Paginación eficiente
- [x] Índices en campos críticos

### **✅ Validaciones y Seguridad**
- [x] Validaciones de integridad referencial
- [x] Manejo de valores nulos en ordenamiento
- [x] Protección CSRF habilitada
- [x] Validación de datos en modelos
- [x] Transacciones atómicas en operaciones masivas

## 📱 Capturas de Pantalla

> **Nota:** Las capturas se pueden agregar ejecutando el sistema y navegando a las URLs principales.

**Dashboard Principal:**
- Vista general con estadísticas y métricas

**Lista de Clientes:**
- Tabla con filtros, búsqueda y ordenamiento

**Detalle de Cliente:**
- Información completa e historial de interacciones

**Lista de Empresas:**
- Gestión de empresas con contadores

## 🔧 Comandos Útiles

### **Desarrollo**
```bash
# Verificar configuración
python manage.py check

# Ver migraciones
python manage.py showmigrations

# Shell interactivo
python manage.py shell

# Recopilar archivos estáticos
python manage.py collectstatic
```

### **Datos de Prueba**
```bash
# Dataset completo (recomendado para demo)
python manage.py populate_data

# Dataset rápido (para desarrollo)
python manage.py populate_data --fast

# Validar datos actuales
python manage.py validate_data --summary

# Limpiar todo
python manage.py clear_data
```

### **Base de Datos**
```bash
# Crear nuevas migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ver SQL de migración
python manage.py sqlmigrate crm_app 0001
```

## 📚 Documentación Adicional

### **Comandos de Gestión**
- `crm_app/management/commands/` - Comandos personalizados
- Documentación integrada con `--help`

### **Configuración**
- `django_app/settings.py` - Configuración principal
- `crm_app/urls.py` - Rutas de la aplicación
- `crm_app/admin.py` - Configuración del panel admin

---

## 🎯 Estado del Proyecto

**✅ FUNCIONALIDAD COMPLETA** - El sistema CRM está completamente implementado y listo para demostración con todas las funcionalidades requeridas:

- ✅ Dashboard con estadísticas
- ✅ Lista de clientes con filtros y ordenamiento completo
- ✅ Detalle de clientes e interacciones
- ✅ Gestión de empresas
- ✅ Interface moderna con Atlantis-Lite
- ✅ 500K+ interacciones generadas
- ✅ Rendimiento optimizado
- ✅ Panel de administración
- ✅ Comandos de gestión de datos

**📊 Datos de Demostración:**
- 3 representantes de ventas
- 50 empresas
- 1,000 clientes
- ~500,000 interacciones

---

**🚀 Desarrollado por:** Luciano Quequezana  
**📅 Última actualización:** Junio 2025  
**💻 Tecnología principal:** Django 5.2.3 + Python 3.12.9
