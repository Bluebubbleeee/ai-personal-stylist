# 🚀 Setup Guide - AI-Powered Personal Stylist

This guide will help you set up the AI-Powered Personal Stylist project on your local machine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13+** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **pip** - Usually comes with Python

## 🔧 Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-personal-stylist.git
cd ai-personal-stylist
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

**Quick Setup (Recommended):**
```bash
python setup_env.py
```

**Manual Setup:**
Create a `.env` file in the project root directory:
```bash
cp env.example .env
```

Then edit `.env` with your actual API keys:
```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Weather API Configuration
WEATHER_API_ENDPOINT=http://api.weatherapi.com/v1/current.json
WEATHER_API_KEY=your_weather_api_key_here

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

📚 **For detailed environment setup, see [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)**

### 5. Database Setup

```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser
```

### 6. Collect Static Files

```bash
python manage.py collectstatic
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

### 8. Access the Application

Open your browser and navigate to:
- **Main Application**: http://127.0.0.1:8000
- **Admin Panel**: http://127.0.0.1:8000/admin

## 🔑 API Keys Setup

### OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

### Weather API Key

1. Visit [WeatherAPI](https://www.weatherapi.com/)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Add the key to your `.env` file

### Email Configuration (Gmail)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use this password in your `.env` file

## 🗄️ Database Configuration

### SQLite (Default - Development)

The project uses SQLite by default, which requires no additional setup.

### PostgreSQL (Production)

For production deployment, configure PostgreSQL:

1. Install PostgreSQL
2. Create a database
3. Update `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🧪 Testing

Run the test suite:

```bash
python manage.py test
```

## 🚀 Deployment

### Production Checklist

1. **Environment Variables**
   - Set `DEBUG=False`
   - Use production database
   - Set secure `SECRET_KEY`
   - Configure production email settings

2. **Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Database**
   ```bash
   python manage.py migrate
   ```

4. **Web Server**
   - Configure Nginx/Apache
   - Set up SSL certificates
   - Configure domain

## 🐛 Troubleshooting

### Common Issues

**1. ModuleNotFoundError**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

**2. Database Issues**
```bash
# Delete database and recreate
rm db.sqlite3
python manage.py migrate
```

**3. Static Files Not Loading**
```bash
# Collect static files
python manage.py collectstatic
```

**4. API Key Issues**
- Verify API keys are correctly set in `.env`
- Check API key permissions and quotas
- Ensure `.env` file is in the project root

**5. Email Not Sending**
- Verify email credentials in `.env`
- Check Gmail App Password is correct
- Ensure 2FA is enabled on Gmail account

### Getting Help

If you encounter issues:

1. Check the [Issues](https://github.com/yourusername/ai-personal-stylist/issues) page
2. Create a new issue with detailed error information
3. Contact support: aistylist@support.com

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [WeatherAPI Documentation](https://www.weatherapi.com/docs/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Happy coding! 🎉**
