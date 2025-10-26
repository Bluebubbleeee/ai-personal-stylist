# AI-Powered Personal Stylist & Wardrobe Manager

<div align="center">
  <img src="https://img.shields.io/badge/Django-5.2.6-green.svg" alt="Django Version">
  <img src="https://img.shields.io/badge/Python-3.13+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/AI-OpenAI-orange.svg" alt="AI Powered">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</div>

<div align="center">
  <h3>🤖 Your intelligent fashion companion powered by cutting-edge AI technology</h3>
  <p>Discover new styles, manage your wardrobe, and get personalized outfit recommendations based on weather, occasion, and your unique preferences.</p>
</div>

---

## 🌟 Features

### 🎯 Core Functionality
- **AI-Powered Recommendations** - Get personalized outfit suggestions using OpenAI Vision API
- **Smart Wardrobe Management** - Organize and categorize your clothing with intelligent tagging
- **Weather-Aware Suggestions** - Real-time weather integration for appropriate outfit recommendations
- **Computer Vision Analysis** - Automatic clothing classification and description generation
- **Style Preferences** - Personalized recommendations based on your favorite colors, styles, and occasions

### 🛠️ Technical Features
- **Responsive Design** - Works seamlessly on desktop, tablet, and mobile devices
- **Real-time Updates** - Dynamic dashboard with live statistics
- **Secure Authentication** - User registration, login, and profile management
- **Image Processing** - Upload and analyze clothing images with AI
- **Database Management** - Efficient data storage and retrieval

### 📱 User Experience
- **Intuitive Interface** - Clean, modern design with Bootstrap 5
- **Interactive Elements** - Hover effects, modals, and smooth transitions
- **Mobile-First** - Optimized for all screen sizes
- **Accessibility** - User-friendly navigation and clear visual hierarchy

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Django 5.2.6
- OpenAI API Key
- WeatherAPI Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-personal-stylist.git
   cd ai-personal-stylist
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000`

---

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root with the following variables:

```env
# OpenAI Configuration
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

### API Keys Setup

1. **OpenAI API Key**
   - Visit [OpenAI Platform](https://platform.openai.com/)
   - Create an account and generate an API key
   - Add the key to your `.env` file

2. **WeatherAPI Key**
   - Visit [WeatherAPI](https://www.weatherapi.com/)
   - Sign up for a free account
   - Get your API key and add it to `.env`

---

## 📁 Project Structure

```
ai-personal-stylist/
├── apps/
│   ├── authentication/          # User authentication and profiles
│   ├── common/                  # Static pages and utilities
│   ├── recommendations/         # AI outfit recommendations
│   └── wardrobe/               # Wardrobe management
├── templates/                   # HTML templates
├── static/                     # CSS, JS, and media files
├── media/                      # User uploaded images
├── stylist_project/            # Django project settings
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

---

## 🎨 Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)
*Real-time weather display and wardrobe statistics*

### Wardrobe Management
![Wardrobe](screenshots/wardrobe.png)
*Smart wardrobe organization with AI-powered categorization*

### AI Recommendations
![Recommendations](screenshots/recommendations.png)
*Personalized outfit suggestions based on weather and preferences*

### Upload with AI Analysis
![Upload](screenshots/upload.png)
*AI-powered clothing analysis and form auto-population*

---

## 🔬 Technology Stack

### Backend
- **Django 5.2.6** - Web framework
- **Python 3.13+** - Programming language
- **SQLite** - Database (development)
- **PostgreSQL** - Database (production ready)

### Frontend
- **Bootstrap 5** - CSS framework
- **JavaScript** - Interactive functionality
- **HTML5/CSS3** - Markup and styling

### AI & APIs
- **OpenAI Vision API** - Clothing analysis and recommendations
- **WeatherAPI** - Real-time weather data
- **Computer Vision** - Image recognition and classification

### Development Tools
- **Django Debug Toolbar** - Development debugging
- **Python Decouple** - Environment variable management
- **Pillow** - Image processing

---

## 🚀 Key Features Deep Dive

### AI-Powered Clothing Analysis
- Upload clothing images for automatic analysis
- AI identifies color, type, style, and season
- Generates detailed descriptions for better recommendations
- Validates clothing items (dress detection)

### Smart Outfit Recommendations
- Considers user's style preferences
- Integrates real-time weather data
- Analyzes wardrobe compatibility
- Provides detailed rationale for each suggestion

### Wardrobe Management
- Digital wardrobe organization
- Favorite items system
- Advanced search and filtering
- Image optimization and storage

### User Experience
- Responsive design for all devices
- Intuitive navigation and user flows
- Real-time updates and notifications
- Professional UI/UX design

---

## 🛡️ Security & Privacy

- **Data Encryption** - All sensitive data is encrypted
- **CSRF Protection** - Cross-site request forgery protection
- **Secure Authentication** - Django's built-in security features
- **Privacy Policy** - Comprehensive data protection guidelines
- **User Consent** - Clear data usage policies

---

## 📊 Performance

- **Optimized Queries** - Efficient database operations
- **Image Optimization** - Compressed and resized images
- **Caching** - Strategic caching for better performance
- **Responsive Loading** - Fast page load times

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 Python style guidelines
- Write comprehensive tests for new features
- Update documentation for any changes
- Ensure all tests pass before submitting PR

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

- **AI Stylist Team** - Core development and AI integration
- **Fashion Experts** - Style consultation and trend analysis
- **UX/UI Designers** - User experience and interface design

---

## 📞 Support

- **Email Support**: aistylist@support.com
- **Phone Support**: +1 (555) 012-3456
- **Documentation**: [Project Wiki](https://github.com/yourusername/ai-personal-stylist/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-personal-stylist/issues)

---

## 🗺️ Roadmap

### Upcoming Features
- [ ] Mobile app (React Native)
- [ ] Social sharing features
- [ ] Advanced analytics dashboard
- [ ] Integration with fashion retailers
- [ ] Voice-activated recommendations
- [ ] AR try-on features

### Version History
- **v1.0.0** - Initial release with core features
- **v1.1.0** - Added weather integration
- **v1.2.0** - Enhanced AI recommendations
- **v1.3.0** - Mobile optimization

---

## 🙏 Acknowledgments

- OpenAI for providing the Vision API
- WeatherAPI for weather data services
- Django community for the excellent framework
- Bootstrap team for the responsive CSS framework
- All contributors and testers

---

<div align="center">
  <p><strong>Made with ❤️ by the AI Stylist Team</strong></p>
  <p>Transform your style with the power of AI</p>
</div>