from django.contrib.auth.models import User
from django.db import models

# User Profile model to extend Django's default User model
class UserProfile(models.Model):
    """Extended user profile with account type"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    account_type = models.CharField(max_length=20, choices=[
        ('customer', 'Customer'),
        ('expert', 'Expert'),
    ], default='customer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Expert-specific fields
    specialization = models.CharField(max_length=100, blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    certification = models.CharField(max_length=200, blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Document upload fields for verification
    certificate_of_practice = models.FileField(upload_to='expert_documents/certificates/', blank=True, null=True)
    id_document = models.FileField(upload_to='expert_documents/ids/', blank=True, null=True)
    verification_notes = models.TextField(blank=True, null=True, help_text='Admin notes for verification')
    
    # Customer-specific fields
    farm_size = models.FloatField(blank=True, null=True)
    primary_crops = models.CharField(max_length=200, blank=True, null=True)
    
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_account_type_display()})"
    
    @property
    def is_customer(self):
        return self.account_type == 'customer'
    
    @property
    def is_expert(self):
        return self.account_type == 'expert'

# Temporarily using Django's default User model
# class User(AbstractUser):
#     """Custom user model with account types"""
#     
#     ACCOUNT_TYPES = [
#         ('customer', 'Customer'),
#         ('expert', 'Expert'),
#     ]
#     
#     account_type = models.CharField(
#         max_length=20,
#         choices=ACCOUNT_TYPES,
#         default='customer',
#         help_text='Type of account - Customer or Expert'
#     )
#     
#     phone_number = models.CharField(max_length=15, blank=True, null=True)
#     location = models.CharField(max_length=100, blank=True, null=True)
#     bio = models.TextField(blank=True, null=True, help_text='Brief description about yourself')
#     
#     # Expert-specific fields
#     specialization = models.CharField(max_length=100, blank=True, null=True, help_text='Area of expertise')
#     experience_years = models.PositiveIntegerField(default=0, help_text='Years of experience')
#     certification = models.CharField(max_length=200, blank=True, null=True, help_text='Professional certifications')
#     hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text='Hourly consultation rate')
#     
#     # Customer-specific fields
#     farm_size = models.FloatField(blank=True, null=True, help_text='Farm size in acres')
#     primary_crops = models.CharField(max_length=200, blank=True, null=True, help_text='Primary crops grown')
#     
#     is_verified = models.BooleanField(default=False, help_text='Account verification status')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     
#     class Meta:
#         db_table = 'auth_user'
#     
#     def __str__(self):
#         return f"{self.username} ({self.get_account_type_display()})"
#     
#     @property
#     def is_customer(self):
#         return self.account_type == 'customer'
#     
#     @property
#     def is_expert(self):
#         return self.account_type == 'expert'
#     
#     def get_full_name(self):
#         if self.first_name and self.last_name:
#             return f"{self.first_name} {self.last_name}"
#         return self.username


class FarmData(models.Model):
    """Model to store farm information and recommendations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    land_size = models.FloatField(help_text="Land size in acres")
    soil_type = models.CharField(max_length=20, choices=[
        ('loamy', 'Loamy'),
        ('clay', 'Clay'),
        ('sandy', 'Sandy'),
        ('silt', 'Silt'),
        ('peat', 'Peat'),
        ('chalky', 'Chalky'),
    ])
    location = models.CharField(max_length=100)
    fertilizer_type = models.CharField(max_length=20, choices=[
        ('organic', 'Organic'),
        ('urea', 'Urea'),
        ('dap', 'DAP'),
        ('npk', 'NPK'),
        ('compost', 'Compost'),
    ])
    water_access = models.CharField(max_length=20, choices=[
        ('rainfed', 'Rainfed'),
        ('irrigation', 'Irrigation'),
        ('mixed', 'Mixed'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Farm Data - {self.location} ({self.land_size} acres)"


class CropRecommendation(models.Model):
    """Model to store crop recommendations"""
    farm_data = models.ForeignKey(FarmData, on_delete=models.CASCADE, related_name='recommendations')
    crop_name = models.CharField(max_length=50)
    suitability_score = models.FloatField(help_text="Suitability score from 0 to 1")
    confidence_level = models.CharField(max_length=20, choices=[
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-suitability_score']
    
    def __str__(self):
        return f"{self.crop_name} - {self.confidence_level} suitability"


class CommunityPost(models.Model):
    """Model for community posts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Post by {self.user.get_full_name()} - {self.created_at.strftime('%Y-%m-%d')}"


class ExpertConsultation(models.Model):
    """Model for expert consultations"""
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultations_as_customer')
    expert = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultations_as_expert')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Consultation: {self.subject} - {self.customer.get_full_name()} & {self.expert.get_full_name()}"