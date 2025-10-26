#!/usr/bin/env python3
"""
Environment Setup Script for AI-Powered Personal Stylist
This script helps users set up their environment variables.
"""

import os
import secrets
import string
from pathlib import Path

def generate_secret_key():
    """Generate a secure Django secret key"""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(alphabet) for _ in range(50))

def create_env_file():
    """Create .env file from template"""
    env_example = Path('env.example')
    env_file = Path('.env')
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("❌ Setup cancelled.")
            return False
    
    if not env_example.exists():
        print("❌ env.example file not found!")
        return False
    
    # Read template
    with open(env_example, 'r') as f:
        content = f.read()
    
    # Replace placeholder values
    content = content.replace('your-secret-key-here', generate_secret_key())
    content = content.replace('your-jwt-secret-here', generate_secret_key())
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ .env file created successfully!")
    return True

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 Environment setup complete!")
    print("="*60)
    print("\n📋 Next steps:")
    print("1. Edit .env file with your actual API keys:")
    print("   - OPENAI_API_KEY: Get from https://platform.openai.com/")
    print("   - WEATHER_API_KEY: Get from https://www.weatherapi.com/")
    print("   - EMAIL_HOST_USER: Your Gmail address")
    print("   - EMAIL_HOST_PASSWORD: Your Gmail App Password")
    print("\n2. Run database migrations:")
    print("   python manage.py makemigrations")
    print("   python manage.py migrate")
    print("\n3. Create superuser:")
    print("   python manage.py createsuperuser")
    print("\n4. Start the development server:")
    print("   python manage.py runserver")
    print("\n📚 For detailed instructions, see ENVIRONMENT_SETUP.md")
    print("="*60)

def main():
    """Main setup function"""
    print("🚀 AI-Powered Personal Stylist - Environment Setup")
    print("="*60)
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Please run this script from the project root directory!")
        return
    
    # Create .env file
    if create_env_file():
        print_next_steps()
    else:
        print("❌ Setup failed!")

if __name__ == "__main__":
    main()
