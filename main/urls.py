# ===== main/urls.py =====
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    # Authentication (Primary Entry Points)
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main pages
    path('home/', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('expert-dashboard/', views.expert_dashboard, name='expert_dashboard'),
    path('edit-expert-profile/', views.edit_expert_profile, name='edit_expert_profile'),
    
    # User-specific pages
    path('my-farm-data/', views.my_farm_data, name='my_farm_data'),
    path('experts/', views.expert_list, name='expert_list'),
    path('respond-consultation/<int:consultation_id>/', views.respond_consultation, name='respond_consultation'),
    
    # API endpoints
    path('api/crop-recommendations/', views.get_crop_recommendations, name='crop_recommendations'),
    path('api/community-posts/', views.create_community_post, name='create_post'),
    path('api/recent-posts/', views.get_recent_posts, name='recent_posts'),
    path('api/request-consultation/', views.request_consultation, name='request_consultation'),
    
    # Weather API endpoints
    path('api/weather/current/', views.get_weather_data, name='weather_current'),
    path('api/weather/forecast/', views.get_weather_forecast, name='weather_forecast'),
    path('api/weather/alerts/', views.get_weather_alerts, name='weather_alerts'),
]