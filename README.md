# 🤖 AI-Powered Personal Stylist & Wardrobe Manager

A comprehensive Django-based web application that leverages artificial intelligence to provide personalized fashion recommendations and intelligent wardrobe management.

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2.6-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-purple.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.2-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

### 🤖 AI-Powered Intelligence
- **Computer Vision Analysis**: OpenAI Vision API integration for automatic clothing classification
- **Smart Recommendations**: AI-generated outfit suggestions based on wardrobe, weather, and preferences
- **Personalized Learning**: System learns from user preferences and style choices
- **Weather-Aware Suggestions**: Real-time weather integration for appropriate outfit recommendations

### 👗 Wardrobe Management
- **Digital Wardrobe**: Upload and organize clothing items with detailed categorization
- **Smart Tagging**: Automatic tagging system with manual override capabilities
- **Image Recognition**: AI-powered analysis of clothing items (color, type, style, etc.)
- **Favorites System**: Mark and filter favorite items for quick access
- **Search & Filter**: Advanced filtering by category, color, season, and more

### 🎨 User Experience
- **Responsive Design**: Mobile-first design that works on all devices
- **Intuitive Interface**: Clean, modern UI with Bootstrap 5
- **Real-time Updates**: Dynamic content updates without page refreshes
- **Professional Styling**: Consistent color scheme and typography throughout

### 🔐 User Management
- **Secure Authentication**: Django's built-in authentication system
- **Profile Management**: Comprehensive user settings and preferences
- **Style Preferences**: Customizable style preferences for better recommendations
- **Email Integration**: Account activation and password reset via email

### 📊 Analytics & Insights
- **Dashboard Analytics**: Overview of wardrobe statistics and recent activity
- **Recommendation History**: Track and review past outfit suggestions
- **Style Analytics**: Insights into personal style patterns and preferences

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- pip (Python package installer)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-personal-stylist.git
   cd ai-personal-stylist
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   
   **Option A: Quick Setup (Recommended)**
   ```bash
   python setup_env.py
   ```
   
   **Option B: Manual Setup**
   Create a `.env` file in the project root:
   ```bash
   cp env.example .env
   ```
   
   Then edit `.env` with your API keys:
   ```env
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
   
   # Django Configuration
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   ```
   
   📚 **For detailed setup instructions, see [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)**

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000`

## 🏗️ Project Structure

```
ai-personal-stylist/
├── apps/
│   ├── authentication/          # User authentication and profiles
│   ├── common/                  # Static pages and shared utilities
│   ├── recommendations/         # AI outfit recommendations
│   └── wardrobe/               # Wardrobe management
├── templates/                   # Django templates
├── static/                     # Static files (CSS, JS, images)
├── media/                      # User-uploaded files
├── stylist_project/            # Django project settings
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
└── README.md                   # This file
```

## 🔧 Configuration

### API Keys Required

1. **OpenAI API Key**
   - Sign up at [OpenAI](https://platform.openai.com/)
   - Generate an API key
   - Add to `.env` file as `OPENAI_API_KEY`

2. **Weather API Key**
   - Sign up at [WeatherAPI](https://www.weatherapi.com/)
   - Get your API key
   - Add to `.env` file as `WEATHER_API_KEY`

3. **Email Configuration**
   - Use Gmail with App Password for SMTP
   - Configure in `.env` file

### Database Configuration

The project uses SQLite by default for development. For production, configure your preferred database in `settings.py`:

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

## 🎯 Usage

### Getting Started

1. **Create an Account**
   - Register a new account or use the admin panel
   - Verify your email address

2. **Build Your Wardrobe**
   - Upload clothing items with photos
   - Let AI analyze and categorize items automatically
   - Add manual details and tags as needed

3. **Get AI Recommendations**
   - Visit the Style Me page
   - Allow location access for weather data
   - Specify occasion and preferences
   - Get personalized outfit suggestions

4. **Manage Your Style**
   - Update your style preferences in Settings
   - Mark favorite items
   - Review recommendation history

### Key Features

- **Upload Items**: Drag and drop or click to upload clothing photos
- **AI Analysis**: Automatic color, type, and style detection
- **Smart Recommendations**: Weather-aware outfit suggestions
- **Wardrobe Organization**: Categorize and filter your clothing
- **Style Preferences**: Customize recommendations to your taste

## 🛠️ Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
```bash
# Check for issues
python manage.py check

# Run linting (if configured)
flake8 .
```

### Database Migrations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## 📱 API Endpoints

### Authentication
- `POST /auth/register/` - User registration
- `POST /auth/login/` - User login
- `POST /auth/logout/` - User logout
- `GET /settings/` - User settings

### Wardrobe Management
- `GET /wardrobe/` - View wardrobe
- `POST /wardrobe/upload/` - Upload clothing item
- `GET /wardrobe/item/<id>/` - Item details
- `POST /wardrobe/item/<id>/edit/` - Edit item
- `DELETE /wardrobe/item/<id>/` - Delete item

### AI Recommendations
- `GET /style-me/` - Style Me page
- `POST /style-me/generate/` - Generate recommendations
- `GET /style-me/suggestion/<id>/` - Suggestion details

### External APIs
- `GET /api/weather/` - Weather data endpoint

## 🔒 Security Features

- **CSRF Protection**: All forms protected against CSRF attacks
- **Secure Authentication**: Django's built-in user authentication
- **Input Validation**: Comprehensive form validation
- **File Upload Security**: Safe handling of user uploads
- **Environment Variables**: Sensitive data stored securely

## 🌐 Deployment

### Production Checklist

1. **Environment Variables**
   - Set `DEBUG=False`
   - Configure production database
   - Set secure `SECRET_KEY`
   - Configure email settings

2. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

3. **Database**
   - Run migrations
   - Create superuser

4. **Web Server**
   - Configure Nginx/Apache
   - Set up SSL certificates
   - Configure domain

### Docker Deployment (Optional)

```dockerfile
FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for the Vision API and GPT models
- **WeatherAPI** for weather data services
- **Django** for the robust web framework
- **Bootstrap** for the responsive UI components
- **Bootstrap Icons** for the icon library

## 📞 Support

- **Email**: aistylist@support.com
- **Phone**: +1 (555) 012-3456
- **Address**: 123 Fashion Avenue, Suite 456, New York, NY 10001

## 🔮 Future Enhancements

- [ ] Mobile app development
- [ ] Social features and sharing
- [ ] Advanced analytics dashboard
- [ ] Integration with fashion retailers
- [ ] Machine learning model improvements
- [ ] Multi-language support
- [ ] Advanced filtering options
- [ ] Outfit planning calendar

---

**Made with ❤️ by the AI Stylist Team**

*Transform your wardrobe with the power of AI!*