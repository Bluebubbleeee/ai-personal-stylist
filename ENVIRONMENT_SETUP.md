# 🔧 Environment Setup Guide

This guide will help you set up the environment variables for the AI-Powered Personal Stylist project.

## 📋 Required Environment Variables

### 1. Create `.env` File

Copy the `env.example` file to create your `.env` file:

```bash
cp env.example .env
```

### 2. Configure Your `.env` File

Edit the `.env` file with your actual API keys and configuration:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Security Settings
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
DEFAULT_FROM_EMAIL=AI Stylist <noreply@aistylist.com>

# OpenAI API Configuration (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here

# Weather API Configuration (REQUIRED)
WEATHER_API_ENDPOINT=http://api.weatherapi.com/v1/current.json
WEATHER_API_KEY=your_weather_api_key_here

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-here
```

## 🔑 API Keys Setup

### OpenAI API Key (Required)

1. **Sign up for OpenAI**
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Create an account or sign in

2. **Generate API Key**
   - Navigate to API Keys section
   - Click "Create new secret key"
   - Copy the key (starts with `sk-proj-`)

3. **Add to `.env`**
   ```env
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```

### Weather API Key (Required)

1. **Sign up for WeatherAPI**
   - Go to [WeatherAPI](https://www.weatherapi.com/)
   - Create a free account

2. **Get API Key**
   - Go to your dashboard
   - Copy your API key

3. **Add to `.env`**
   ```env
   WEATHER_API_KEY=your_weather_api_key_here
   ```

### Email Configuration (Optional)

1. **Gmail Setup**
   - Enable 2-Factor Authentication on your Gmail account
   - Generate an App Password:
     - Go to Google Account settings
     - Security → 2-Step Verification → App passwords
     - Generate password for "Mail"

2. **Add to `.env`**
   ```env
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_16_character_app_password
   ```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
```bash
# Copy example file
cp env.example .env

# Edit with your API keys
# (Use your preferred text editor)
nano .env
# or
code .env
```

### 3. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Start Development Server
```bash
python manage.py runserver
```

## 🔒 Security Best Practices

### 1. Never Commit `.env` Files
- The `.env` file is already in `.gitignore`
- Never commit API keys to version control

### 2. Use Strong Secret Keys
- Generate a strong Django secret key
- Use a random string generator for JWT secret

### 3. Environment-Specific Configuration
- Use different `.env` files for different environments
- Example: `.env.development`, `.env.production`

## 🧪 Testing Configuration

### Test OpenAI API
```bash
python manage.py shell
>>> from apps.wardrobe.computer_vision_api import test_openai_api
>>> test_openai_api()
```

### Test Weather API
```bash
python manage.py shell
>>> from apps.recommendations.weather_service import WeatherService
>>> ws = WeatherService()
>>> ws.get_weather_data("New York")
```

## 🐛 Troubleshooting

### Common Issues

**1. OpenAI API Key Not Working**
- Verify the key is correct and active
- Check your OpenAI account has credits
- Ensure the key starts with `sk-proj-`

**2. Weather API Not Working**
- Verify the API key is correct
- Check your WeatherAPI account status
- Ensure you haven't exceeded the free tier limits

**3. Email Not Sending**
- Verify Gmail App Password is correct
- Check 2FA is enabled on Gmail
- Ensure the password is 16 characters long

**4. Environment Variables Not Loading**
- Ensure `.env` file is in the project root
- Check file permissions
- Restart the Django server after changes

### Debug Environment Variables

```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.OPENAI_API_KEY)
>>> print(settings.WEATHER_API_KEY)
```

## 📚 Additional Resources

- [Django Environment Variables](https://docs.djangoproject.com/en/stable/topics/settings/#environment-variables)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [WeatherAPI Documentation](https://www.weatherapi.com/docs/)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)

---

**Need Help?** Contact us at aistylist@support.com
