# Setup Guide - AI-Powered Personal Stylist

This guide will help you set up the AI-Powered Personal Stylist project on your local machine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13+** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Code Editor** - VS Code, PyCharm, or any preferred editor

## 🔑 Required API Keys

You'll need to obtain the following API keys:

### 1. OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (you won't be able to see it again)

### 2. WeatherAPI Key
1. Visit [WeatherAPI](https://www.weatherapi.com/)
2. Sign up for a free account
3. Go to your dashboard
4. Copy your API key

### 3. Gmail App Password (for email functionality)
1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account settings
3. Navigate to Security > App passwords
4. Generate a new app password for "Mail"
5. Use this password in your .env file

## 🚀 Installation Steps

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/ai-personal-stylist.git
cd ai-personal-stylist
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
1. Copy the example environment file:
   ```bash
   copy .env.example .env  # Windows
   cp .env.example .env    # macOS/Linux
   ```

2. Edit the `.env` file with your actual values:
   ```env
   # Django Configuration
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   
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
   EMAIL_HOST_PASSWORD=your_gmail_app_password
   ```

### Step 5: Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Step 6: Run the Server
```bash
python manage.py runserver
```

### Step 7: Access the Application
Open your browser and navigate to: `http://127.0.0.1:8000`

## 🧪 Testing the Setup

### 1. Create an Account
- Click "Sign Up" on the homepage
- Fill in your details and verify your email

### 2. Upload a Clothing Item
- Go to Wardrobe > Upload Item
- Upload an image of a dress or clothing item
- Verify that AI analysis populates the form

### 3. Get AI Recommendations
- Go to Style Me page
- Allow location access for weather data
- Request outfit recommendations

### 4. Test All Features
- Browse your wardrobe
- Mark items as favorites
- Edit item details
- Check dashboard statistics

## 🔧 Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError" when running commands
**Solution**: Ensure your virtual environment is activated
```bash
# Check if venv is activated (you should see (venv) in your terminal)
# If not, activate it:
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

#### 2. "API key not found" errors
**Solution**: Check your `.env` file
- Ensure the file is named exactly `.env` (not `.env.txt`)
- Verify all API keys are correctly entered
- Restart the Django server after making changes

#### 3. Email not sending
**Solution**: Check email configuration
- Ensure you're using an App Password, not your regular Gmail password
- Verify 2FA is enabled on your Gmail account
- Check that EMAIL_HOST_USER is your full Gmail address

#### 4. Weather data not loading
**Solution**: Check WeatherAPI configuration
- Verify your API key is correct
- Ensure you have API calls remaining in your quota
- Check browser console for JavaScript errors

#### 5. Images not displaying
**Solution**: Check media file configuration
- Ensure the `media/` directory exists
- Check file permissions
- Verify MEDIA_URL and MEDIA_ROOT settings

### Debug Mode
If you encounter issues, you can enable debug mode by setting `DEBUG=True` in your `.env` file. This will show detailed error messages.

## 📁 Project Structure

```
ai-personal-stylist/
├── apps/                    # Django applications
│   ├── authentication/     # User management
│   ├── common/            # Static pages
│   ├── recommendations/   # AI recommendations
│   └── wardrobe/          # Wardrobe management
├── templates/             # HTML templates
├── static/               # CSS, JS, images
├── media/                # User uploaded files
├── stylist_project/      # Django settings
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
├── LICENSE             # MIT License
├── README.md           # Project documentation
└── SETUP.md           # This file
```

## 🚀 Deployment

### For Production Deployment

1. **Set Production Environment Variables**:
   ```env
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Use Production Database**:
   - PostgreSQL recommended for production
   - Update DATABASE_URL in .env

3. **Static Files**:
   ```bash
   python manage.py collectstatic
   ```

4. **Security Settings**:
   - Set secure cookies
   - Use HTTPS
   - Configure proper CORS settings

## 📞 Support

If you encounter any issues during setup:

1. Check this troubleshooting guide
2. Review the [GitHub Issues](https://github.com/yourusername/ai-personal-stylist/issues)
3. Contact support: aistylist@support.com

## 🎉 You're All Set!

Once you've completed these steps, you should have a fully functional AI-Powered Personal Stylist running on your local machine. Enjoy exploring the features and building your digital wardrobe!
