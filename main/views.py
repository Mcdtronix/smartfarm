from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
import json
from .models import FarmData, CropRecommendation, CommunityPost, ExpertConsultation, UserProfile
from django.contrib.auth.models import User
from .ml_service import crop_service
from .weather_service import weather_service

def index(request):
    """Main homepage view"""
    # Get recent community posts
    recent_posts = CommunityPost.objects.all()[:5]
    
    context = {
        'recent_posts': recent_posts,
    }
    return render(request, 'main/index.html', context)

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        account_type = request.POST.get('account_type', 'customer')
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'main/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'main/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'main/register.html')
        
        # Create user with basic fields only
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create user profile with account type
        UserProfile.objects.create(
            user=user,
            account_type=account_type,
            location=request.POST.get('location', '')
        )
        
        if account_type == 'expert':
            messages.success(request, f'Welcome {user.get_full_name()}! Your expert account has been created successfully. Please log in to access your expert dashboard.')
            return redirect('main:login')
        else:
            # Auto-login after registration for customers
            login(request, user)
            messages.success(request, f'Welcome {user.get_full_name()}! Your account has been created successfully.')
            return redirect('main:dashboard')
    
    return render(request, 'main/register.html')

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            
            # Check if user is an expert and redirect accordingly
            try:
                profile = user.profile
                if profile.is_expert:
                    return redirect('main:expert_dashboard')
                else:
                    return redirect('main:dashboard')
            except UserProfile.DoesNotExist:
                # If no profile exists, treat as customer
                return redirect('main:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'main/login.html')

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('main:login')

@login_required
def dashboard(request):
    """Customer dashboard view"""
    user = request.user
    
    # Check if user is an expert, redirect to expert dashboard
    try:
        profile = user.profile
        if profile.is_expert:
            return redirect('main:expert_dashboard')
    except UserProfile.DoesNotExist:
        pass
    
    # Customer dashboard data
    farm_data = FarmData.objects.filter(user=user).order_by('-created_at')[:5]
    recent_posts = CommunityPost.objects.filter(user=user).order_by('-created_at')[:5]
    consultations = ExpertConsultation.objects.filter(customer=user).order_by('-created_at')[:5]
    
    context = {
        'farm_data': farm_data,
        'recent_posts': recent_posts,
        'consultations': consultations,
    }
    return render(request, 'main/customer_dashboard.html', context)

@login_required
def expert_dashboard(request):
    """Expert dashboard view"""
    user = request.user
    
    # Check if user is an expert
    try:
        profile = user.profile
        if not profile.is_expert:
            messages.error(request, 'Access denied. This dashboard is for experts only.')
            return redirect('main:dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Access denied. This dashboard is for experts only.')
        return redirect('main:dashboard')
    
    # Get consultations directed to this expert
    consultations = ExpertConsultation.objects.filter(expert=user).order_by('-created_at')
    
    # Statistics
    total_consultations = consultations.count()
    pending_consultations = consultations.filter(status='pending').count()
    active_consultations = consultations.filter(status__in=['accepted', 'in_progress']).count()
    completed_consultations = consultations.filter(status='completed').count()
    
    context = {
        'consultations': consultations[:10],  # Show recent 10
        'total_consultations': total_consultations,
        'pending_consultations': pending_consultations,
        'active_consultations': active_consultations,
        'completed_consultations': completed_consultations,
        'profile': profile,
    }
    return render(request, 'main/expert_dashboard.html', context)

@login_required
def respond_consultation(request, consultation_id):
    """Expert response to consultation"""
    user = request.user
    
    # Check if user is an expert
    try:
        profile = user.profile
        if not profile.is_expert:
            messages.error(request, 'Access denied. Only experts can respond to consultations.')
            return redirect('main:dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Access denied. Only experts can respond to consultations.')
        return redirect('main:dashboard')
    
    try:
        consultation = ExpertConsultation.objects.get(id=consultation_id, expert=user)
    except ExpertConsultation.DoesNotExist:
        messages.error(request, 'Consultation not found.')
        return redirect('main:expert_dashboard')
    
    if request.method == 'POST':
        response_text = request.POST.get('response_text')
        new_status = request.POST.get('status')
        
        if response_text:
            # Update consultation with response
            consultation.status = new_status
            consultation.save()
            
            # Here you could add a ConsultationResponse model to store the response
            # For now, we'll just update the status
            
            messages.success(request, 'Your response has been submitted successfully.')
            return redirect('main:expert_dashboard')
        else:
            messages.error(request, 'Response text is required.')
    
    context = {
        'consultation': consultation,
    }
    return render(request, 'main/respond_consultation.html', context)

@login_required
def edit_expert_profile(request):
    """Edit expert profile and upload documents"""
    user = request.user
    
    # Check if user is an expert
    try:
        profile = user.profile
        if not profile.is_expert:
            messages.error(request, 'Access denied. Only experts can edit this profile.')
            return redirect('main:dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Access denied. Only experts can edit this profile.')
        return redirect('main:dashboard')
    
    if request.method == 'POST':
        # Update profile fields
        profile.specialization = request.POST.get('specialization', '')
        profile.experience_years = int(request.POST.get('experience_years', 0))
        profile.certification = request.POST.get('certification', '')
        profile.hourly_rate = request.POST.get('hourly_rate') or None
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        profile.phone_number = request.POST.get('phone_number', '')
        
        # Handle file uploads
        if 'certificate_of_practice' in request.FILES:
            profile.certificate_of_practice = request.FILES['certificate_of_practice']
        
        if 'id_document' in request.FILES:
            profile.id_document = request.FILES['id_document']
        
        profile.save()
        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('main:expert_dashboard')
    
    context = {
        'profile': profile,
    }
    return render(request, 'main/edit_expert_profile.html', context)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def get_crop_recommendations(request):
    """API endpoint for getting crop recommendations"""
    try:
        data = json.loads(request.body)
        
        # Extract form data
        land_size = float(data.get('land_size', 0))
        soil_type = data.get('soil_type', '')
        location = data.get('location', '')
        fertilizer_type = data.get('fertilizer_type', '')
        water_access = data.get('water_access', '')
        
        # Validate required fields
        if not all([land_size, soil_type, fertilizer_type, water_access]):
            return JsonResponse({
                'success': False,
                'error': 'All fields are required'
            })
        
        # Get ML recommendations
        recommendations = crop_service.get_recommendations(
            land_size=land_size,
            soil_type=soil_type,
            fertilizer_type=fertilizer_type,
            water_access=water_access,
            location=location
        )
        
        # Save farm data and recommendations to database
        farm_data = FarmData.objects.create(
            user=request.user,
            land_size=land_size,
            soil_type=soil_type,
            location=location,
            fertilizer_type=fertilizer_type,
            water_access=water_access
        )
        
        # Save recommendations
        for rec in recommendations:
            CropRecommendation.objects.create(
                farm_data=farm_data,
                crop_name=rec['crop_name'],
                suitability_score=rec['suitability_score'],
                confidence_level=rec['confidence_level']
            )
        
        return JsonResponse({
            'success': True,
            'recommendations': recommendations,
            'farm_data_id': farm_data.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_community_post(request):
    """API endpoint for creating community posts"""
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({
                'success': False,
                'error': 'Content cannot be empty'
            })
        
        # Create community post
        post = CommunityPost.objects.create(
            user=request.user,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'post': {
                'id': post.id,
                'author_name': post.user.get_full_name(),
                'content': post.content,
                'created_at': post.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

def get_recent_posts(request):
    """API endpoint for getting recent community posts"""
    try:
        posts = CommunityPost.objects.all()[:10]
        posts_data = []
        
        for post in posts:
            posts_data.append({
                'id': post.id,
                'author_name': post.user.get_full_name(),
                'content': post.content,
                'created_at': post.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'posts': posts_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

@login_required
def my_farm_data(request):
    """View user's farm data and recommendations"""
    farm_data = FarmData.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'farm_data': farm_data,
    }
    return render(request, 'main/my_farm_data.html', context)

@login_required
def expert_list(request):
    """List of available experts"""
    # Only show users with expert profiles
    experts = User.objects.filter(
        is_active=True,
        profile__account_type='expert'
    ).select_related('profile').order_by('-date_joined')
    
    context = {
        'experts': experts,
    }
    return render(request, 'main/expert_list.html', context)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def request_consultation(request):
    """Request consultation with an expert"""
    try:
        data = json.loads(request.body)
        expert_id = data.get('expert_id')
        subject = data.get('subject', '').strip()
        description = data.get('description', '').strip()
        
        if not all([expert_id, subject, description]):
            return JsonResponse({
                'success': False,
                'error': 'All fields are required'
            })
        
        expert = User.objects.get(
            id=expert_id, 
            is_active=True,
            profile__account_type='expert'
        )
        
        consultation = ExpertConsultation.objects.create(
            customer=request.user,
            expert=expert,
            subject=subject,
            description=description
        )
        
        return JsonResponse({
            'success': True,
            'consultation_id': consultation.id,
            'message': 'Consultation request sent successfully'
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Expert not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_weather_data(request):
    """API endpoint for getting current weather data"""
    try:
        city = request.GET.get('city', 'Harare')  # Default to Harare, Zimbabwe
        country = request.GET.get('country', 'ZW')  # Default to Zimbabwe
        
        # Get current weather
        current_weather = weather_service.get_current_weather(city, country)
        
        if not current_weather['success']:
            return JsonResponse(current_weather)
        
        return JsonResponse({
            'success': True,
            'current_weather': current_weather['data']
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_weather_forecast(request):
    """API endpoint for getting weather forecast"""
    try:
        city = request.GET.get('city', 'Harare')  # Default to Harare, Zimbabwe
        country = request.GET.get('country', 'ZW')  # Default to Zimbabwe
        days = int(request.GET.get('days', 7))  # Default to 7 days
        
        # Get forecast
        forecast = weather_service.get_forecast(city, country, days)
        
        if not forecast['success']:
            return JsonResponse(forecast)
        
        return JsonResponse({
            'success': True,
            'forecast': forecast['data']
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["GET"])
def get_weather_alerts(request):
    """API endpoint for getting weather alerts and agricultural advice"""
    try:
        city = request.GET.get('city', 'Harare')  # Default to Harare, Zimbabwe
        country = request.GET.get('country', 'ZW')  # Default to Zimbabwe
        
        # Get weather alerts
        alerts = weather_service.get_weather_alerts(city, country)
        
        if not alerts['success']:
            return JsonResponse(alerts)
        
        return JsonResponse({
            'success': True,
            'alerts': alerts['data']['alerts'],
            'current_weather': alerts['data']['current_weather']
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })