# PPST Django Backend

Backend API for the Philadelphia Pointing Span Test application built with Django and Django REST Framework.

## Project Structure

```
backend/
├── manage.py                  # Django CLI management script
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── ppst/                     # Main project configuration
│   ├── __init__.py
│   ├── settings.py           # Django settings
│   ├── urls.py              # Main URL routing
│   ├── wsgi.py              # WSGI application entry
│   └── asgi.py              # ASGI application entry
├── api/                      # Main Django application (keep unchanged for now)
│   ├── __init__.py
│   ├── apps.py              # App configuration
│   ├── models.py            # Database models
│   ├── views.py             # API views/viewsets
│   ├── urls.py              # App URL routing
│   ├── serializers.py       # DRF serializers
│   ├── admin.py             # Django admin configuration
│   └── migrations/          # Database migrations
├── accounts/                 # Placeholder app (future split)
│   ├── __init__.py
│   ├── apps.py
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── migrations/
│   └── templates/
├── portal/                   # Placeholder app (future split)
│   ├── __init__.py
│   ├── apps.py
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── migrations/
│   └── templates/
├── patient/                  # Placeholder app (future split)
│   ├── __init__.py
│   ├── apps.py
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── migrations/
│   └── templates/
└── testapp/                  # Placeholder app (future split)
    ├── __init__.py
    ├── apps.py
    ├── admin.py
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── migrations/
    └── templates/
```

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Creating an active virtual environment
# Windows
```bash
python -m venv venv
venv\Scripts\activate
```
# Mac/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` file** (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000`

## Common Commands

```bash
# Create new app
python manage.py startapp app_name

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Access admin panel
# Go to http://localhost:8000/admin

# Run tests
python manage.py test

# Shell access
python manage.py shell
```

## API Endpoints

Base URL: `http://localhost:8000/api/`

- Admin Panel: `http://localhost:8000/admin/`

## Database

By default, this project uses SQLite3 for development. To switch to PostgreSQL:

1. Update `DB_ENGINE` and other database credentials in `.env`
2. Update `DATABASES` in `ppst/settings.py`
3. Run migrations with PostgreSQL

## CORS Configuration

CORS is configured to allow requests from the Next.js frontend running on `http://localhost:3000`.

Edit `CORS_ALLOWED_ORIGINS` in `ppst/settings.py` to add more allowed origins.

## Adding New Models to the Backend

### Step 1: Choose the Right App
Place your model in the appropriate app based on its purpose:

- **`accounts/`** — User/doctor account models
- **`portal/`** — Portal/dashboard models
- **`patient/`** — Patient/test subject models
- **`testapp/`** — Test session/stimulus/response models
- **`api/`** — Legacy API models (already contains `Doctor`)

Example: If adding a `Patient` model, place it in `patient/models.py`

### Step 2: Define Your Model
Create your model class in `{app}/models.py`:

```python
from django.db import models

class YourModel(models.Model):
    """Description of your model."""
    field1 = models.CharField(max_length=150)
    field2 = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'your_model_table'  # Optional: specify table name
    
    def __str__(self):
        return f"YourModel: {self.field1}"
```

**Note:** Follow the pattern used by the `Doctor` model in `api/models.py`. For password fields, use Django's `make_password()` and `check_password()` utilities.

### Step 3: Register in Django Admin
Add your model to `{app}/admin.py` so it appears in the Django admin panel:

```python
from django.contrib import admin
from .models import YourModel

admin.site.register(YourModel)
```

### Step 4: Create DRF Serializer (if using REST APIs)
Define a serializer in `{app}/serializers.py`:

```python
from rest_framework import serializers
from .models import YourModel

class YourModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YourModel
        fields = '__all__'  # or specify: ['field1', 'field2', ...]
```

### Step 5: Create REST API Views (if using REST APIs)
Define viewsets in `{app}/views.py`:

```python
from rest_framework import viewsets
from .models import YourModel
from .serializers import YourModelSerializer

class YourModelViewSet(viewsets.ModelViewSet):
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer
```

### Step 6: Register API Routes (if using REST APIs)
Update `{app}/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'your-models', views.YourModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

### Step 7: Include App Routes in Main URL Config
If the app has new routes, update `config/urls.py` to include them:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('patient/', include('patient.urls')),  # Add new app routes
    # ... add other apps as needed
]
```

### Step 8: Create Migrations
Generate migration files for your new model:

```bash
python manage.py makemigrations
```

This creates a migration file in `{app}/migrations/` that tracks your model changes.

### Step 9: Apply Migrations
Apply the migrations to the database:

```bash
python manage.py migrate
```

### Complete Workflow Example (from start to finish)

1. Define model in `patient/models.py`
2. Register in `patient/admin.py`
3. Create serializer in `patient/serializers.py`
4. Create viewset in `patient/views.py`
5. Setup routes in `patient/urls.py`
6. Include routes in `config/urls.py`
7. Run `python manage.py makemigrations`
8. Run `python manage.py migrate`
9. Commit changes:

```bash
python manage.py makemigrations
python manage.py migrate
git add patient/models.py patient/serializers.py patient/views.py patient/admin.py patient/urls.py patient/migrations/
git commit -m "Add Patient model with REST API endpoints"
git push
```

### Backend Development Workflow
1. python manage.py makemigrations
2. python manage.py migrate
3. git add {app}/migrations/
4. git commit -m "Tell us what you did in your commit"
5. git push

## Pulling new changes
1. git pull
2. python manage.py migrate

### DO NOT COMMIT THESE FILES
# Ignoring these files prevents database conflicts!!
```
db.sqlite3
venv/
__pycache__/
.env
```

### Code placement
        Database models -> api/models.py
            Serializers -> api/serializers.py
     API views/viewsets -> api/views.py
              APP routs -> api/urls.py
     Admin registration -> api/admin.py

 Custom Django commands -> api/management/comands
 
Algorithms / PPST logic -> ppst_methods/
