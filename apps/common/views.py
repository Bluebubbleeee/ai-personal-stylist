from django.shortcuts import render

def about_view(request):
    """About Us page"""
    return render(request, 'common/about.html')

def privacy_view(request):
    """Privacy Policy page"""
    return render(request, 'common/privacy.html')

def terms_view(request):
    """Terms of Service page"""
    return render(request, 'common/terms.html')

def contact_view(request):
    """Contact Us page"""
    return render(request, 'common/contact.html')
