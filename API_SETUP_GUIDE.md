# 🔑 API Keys Configuration Guide

## Quick Setup for Your AI Stylist Project

### 📁 **Main Configuration File: `.env`**
All your API keys and settings go in the `.env` file in your project root.

---

## 🚀 **Step 1: Get Your API Keys**

### 1. **Computer Vision API** (for auto-tagging clothes)
**Options:**
- **Google Cloud Vision API** (Recommended)
  - Go to: https://cloud.google.com/vision
  - Free tier: 1,000 requests/month
  - Get API key and replace `CV_API_ENDPOINT` & `CV_API_KEY`

- **Azure Computer Vision**
  - Go to: https://azure.microsoft.com/en-us/services/cognitive-services/computer-vision/
  - Student credits available
  - Get endpoint and key

### 2. **Weather API** (for weather-based recommendations)
**OpenWeatherMap (Recommended):**
- Go to: https://openweathermap.org/api
- **FREE tier**: 1,000 calls/day
- Sign up → Get API key
- Replace `WEATHER_API_KEY=xxxxxx` with your key
- Keep endpoint as: `https://api.openweathermap.org/data/2.5`

### 3. **AI Recommendation API** (for outfit suggestions)
**Options:**
- **OpenAI API**
  - Go to: https://platform.openai.com/
  - Get API key for ChatGPT/GPT-4
  - Replace `AI_RECOMMENDATION_API_KEY=xxxxxx`

- **Anthropic Claude**
  - Go to: https://console.anthropic.com/
  - Get API key for Claude
  - Update endpoint accordingly

### 4. **Email Service** (for account activation)
**Gmail (Easiest for students):**
- Use your Gmail account
- Enable "2-Step Verification"
- Generate "App Password" (not your regular password!)
- Replace `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`

---

## 🔧 **Step 2: Configure `.env` File**

Open `.env` file and replace all `xxxxxx` values:

```env
# Replace these with your actual values:
SECRET_KEY=your-really-long-secret-key-here
DEBUG=True
WEATHER_API_KEY=your_openweathermap_key_here
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password_here
CV_API_KEY=your_computer_vision_api_key
AI_RECOMMENDATION_API_KEY=your_openai_or_claude_key
```

---

## 🎓 **For University Demo (Without Real APIs)**

If you want to demo without setting up APIs, you can use **MOCK mode**:

1. Keep the `xxxxxx` values as they are
2. The system will automatically use mock responses
3. Perfect for presentations and testing!

---

## 🗂️ **Project Structure for Configuration**

```
Your Project/
├── .env                    ← YOUR API KEYS GO HERE!
├── env.example             ← Template (don't edit)
├── stylist_project/
│   └── settings.py         ← Reads from .env
├── manage.py
└── requirements.txt
```

---

## ⚡ **Quick Start Commands**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure your API keys in .env file
# (Edit .env with your actual keys)

# 3. Run migrations
python manage.py migrate

# 4. Start the server
python manage.py runserver

# 5. Visit your AI Stylist!
# http://127.0.0.1:8000/
```

---

## 💡 **Pro Tips for University Projects**

1. **For Demo**: Use mock APIs (keep `xxxxxx` values)
2. **For Real Testing**: Get free tier API keys
3. **For Production**: Upgrade to paid APIs
4. **Security**: Never commit real API keys to Git!

---

## 🔒 **Security Notes**

- ✅ `.env` file is in `.gitignore` (safe)
- ✅ Never share your real API keys
- ✅ Use different keys for development vs production
- ✅ Regenerate keys if accidentally exposed

---

## 🆘 **Need Help?**

**Common Issues:**
- **Email not working?** Make sure you use Gmail App Password, not regular password
- **Weather API failing?** Check if your OpenWeatherMap key is activated (takes 10 min)
- **Mock mode?** Just leave `xxxxxx` values - the system will simulate responses

**Everything works without real APIs for demonstration purposes!** 🎉
