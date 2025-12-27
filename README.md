# Kiron Accounting Software - Backend API

A Django REST Framework backend for managing tuition house operations, including user authentication, profile management, and more.


## 🛠️ Tech Stack

- **Django 5.2.8**: High-level Python web framework
- **Django REST Framework**: Powerful toolkit for building Web APIs
- **dj-rest-auth**: Authentication endpoints for DRF
- **Simple JWT**: JSON Web Token authentication
- **drf-spectacular**: OpenAPI 3.0 schema generation and documentation
- **django-resized**: Image resizing and optimization
- **django-cleanup**: Automatic cleanup of old files
- **django-cors-headers**: CORS handling
- **Pillow**: Python Imaging Library for image processing

## 📋 Prerequisites

- Python 3.10+
- pip (Python package manager)
- Virtual environment (recommended)

## 🔧 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Bigmod-Technologies/kas-be
cd kas-be
```

### 2. Create and activate virtual environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### Generating a Secret Key

You can generate a secure Django secret key using any of these methods:

**Method 1: Using Django (Recommended)**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Method 2: Using Python's secrets module**

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

**Method 3: Online Generator**
Visit [Djecrety.ir](https://djecrety.ir/) to generate a secure key online.

> [!IMPORTANT]
> Never commit your `.env` file or expose your `SECRET_KEY` in version control. Add `.env` to your `.gitignore` file.

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## 📚 API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **ReDoc**: [http://127.0.0.1:8000/doc/](http://127.0.0.1:8000/doc/)
- **OpenAPI Schema**: [http://127.0.0.1:8000/schema/](http://127.0.0.1:8000/schema/)

### Using Authentication

Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

## 🔒 Admin Panel

Access the Django admin panel at `http://127.0.0.1:8000/admin/`

Features:

- User management (create, edit, delete)
- Profile picture upload with delete option
- Search by username, email, or mobile number
- Permission management

## 🧪 Running Tests

```bash

```

## 📦 Dependencies

Key packages (see full list in `requirements.txt`):

- Django
- djangorestframework
- dj-rest-auth
- djangorestframework-simplejwt
- drf-spectacular
- django-cors-headers
- django-filter
- django-resized
- django-cleanup
- daphne
- Pillow

## 🚀 Deployment

### Production Checklist

1. Set `DEBUG = False` in settings
2. Update `ALLOWED_HOSTS` with your domain
3. Set a strong `SECRET_KEY` (use environment variable)
4. Configure a production database (PostgreSQL recommended)
5. Set up static files serving
6. Configure media files storage (AWS S3, etc.)
7. Enable HTTPS
8. Set up proper CORS settings
9. Configure logging
10. Use environment variables for sensitive data

### Environment Variables

Create a `.env` file for production:

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

- Light Bulb Quest Team

## 📧 Contact

For questions or support, please contact the development team.

## 🐛 Known Issues

None at the moment. Please report any bugs in the Issues section.

## 🙏 Acknowledgments

- Django Software Foundation
- Django REST Framework team
- All contributors and supporters
