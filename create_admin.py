#!/usr/bin/env python
"""
Django Admin Setup Script for FarmSmart
This script helps create a superuser for Django admin access
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmsmart_project.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import UserProfile

def create_superuser():
    """Create a superuser for Django admin access"""
    print("Creating Django superuser for FarmSmart admin...")
    
    username = input("Enter username (default: admin): ").strip() or "admin"
    email = input("Enter email (default: admin@farmsmart.com): ").strip() or "admin@farmsmart.com"
    password = input("Enter password (default: admin123): ").strip() or "admin123"
    
    # Create superuser
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists!")
        return
    
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name="Admin",
        last_name="User"
    )
    
    # Create profile for the superuser
    UserProfile.objects.create(
        user=user,
        account_type='expert',  # Admin can be considered an expert
        is_verified=True,
        specialization="System Administration",
        experience_years=10,
        location="System",
        bio="System administrator for FarmSmart platform"
    )
    
    print(f"✅ Superuser '{username}' created successfully!")
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
    print("\n🌐 Access Django Admin at: http://127.0.0.1:8000/admin/")
    print("📋 Admin Features Available:")
    print("   • User Profile Management")
    print("   • Expert Verification")
    print("   • Document Review")
    print("   • Consultation Management")
    print("   • Bulk Actions")

def show_admin_features():
    """Display available admin features"""
    print("\n🔧 Django Admin Features for Expert Verification:")
    print("=" * 50)
    print("1. 📊 User Profiles Management")
    print("   • View all user profiles")
    print("   • Filter by account type (Expert/Customer)")
    print("   • Search by name, email, specialization")
    print("   • View verification status")
    print()
    print("2. ✅ Expert Verification")
    print("   • Verify/unverify experts individually")
    print("   • Bulk verification actions")
    print("   • Add verification notes")
    print("   • View uploaded documents")
    print()
    print("3. 📄 Document Management")
    print("   • View certificate of practice")
    print("   • View ID documents")
    print("   • Download verification documents")
    print("   • Track document upload status")
    print()
    print("4. 💬 Consultation Management")
    print("   • View all consultation requests")
    print("   • Update consultation status")
    print("   • Filter by status and date")
    print("   • Bulk status updates")
    print()
    print("5. 📈 Analytics & Reports")
    print("   • Export expert lists")
    print("   • View verification statistics")
    print("   • Track consultation metrics")

if __name__ == "__main__":
    print("🌱 FarmSmart Django Admin Setup")
    print("=" * 40)
    
    try:
        create_superuser()
        show_admin_features()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Django is properly configured and migrations are run.")
