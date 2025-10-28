from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import FarmData, CropRecommendation, CommunityPost, ExpertConsultation, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Using Django's default User admin
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ['username', 'email', 'account_type', 'first_name', 'last_name', 'is_verified', 'is_active']
#     list_filter = ['account_type', 'is_verified', 'is_active', 'created_at']
#     search_fields = ['username', 'email', 'first_name', 'last_name']
#     readonly_fields = ['created_at', 'updated_at']
#     
#     fieldsets = (
#         ('Basic Information', {
#             'fields': ('username', 'email', 'first_name', 'last_name', 'account_type')
#         }),
#         ('Contact Information', {
#             'fields': ('phone_number', 'location', 'bio')
#         }),
#         ('Expert Information', {
#             'fields': ('specialization', 'experience_years', 'certification', 'hourly_rate'),
#             'classes': ('collapse',)
#         }),
#         ('Customer Information', {
#             'fields': ('farm_size', 'primary_crops'),
#             'classes': ('collapse',)
#         }),
#         ('Account Status', {
#             'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser')
#         }),
#         ('Timestamps', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         })
#     )

# UserProfile Admin Configuration
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'account_type', 'phone_number', 'location', 'bio',
        'specialization', 'experience_years', 'certification', 'hourly_rate',
        'farm_size', 'primary_crops', 'is_verified', 'verification_notes',
        'certificate_of_practice', 'id_document'
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user_info', 'account_type', 'specialization', 'experience_years', 
        'verification_status', 'location', 'created_at'
    ]
    list_filter = [
        'account_type', 'is_verified', 'created_at', 'experience_years'
    ]
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 'user__last_name',
        'specialization', 'location', 'certification'
    ]
    readonly_fields = ['created_at', 'updated_at', 'document_links']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'account_type', 'phone_number', 'location', 'bio')
        }),
        ('Expert Information', {
            'fields': ('specialization', 'experience_years', 'certification', 'hourly_rate'),
            'classes': ('collapse',)
        }),
        ('Customer Information', {
            'fields': ('farm_size', 'primary_crops'),
            'classes': ('collapse',)
        }),
        ('Verification Documents', {
            'fields': ('certificate_of_practice', 'id_document', 'document_links'),
            'classes': ('collapse',)
        }),
        ('Verification Status', {
            'fields': ('is_verified', 'verification_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['verify_experts', 'unverify_experts', 'export_expert_list']
    
    def user_info(self, obj):
        """Display user information with link to user admin"""
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html(
            '<a href="{}">{} ({})</a>',
            url,
            obj.user.get_full_name() or obj.user.username,
            obj.user.email
        )
    user_info.short_description = 'User'
    user_info.admin_order_field = 'user__username'
    
    def verification_status(self, obj):
        """Display verification status with color coding"""
        if obj.is_verified:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Verified</span>'
            )
        else:
            return format_html(
                '<span style="color: orange; font-weight: bold;">⏳ Pending</span>'
            )
    verification_status.short_description = 'Verification Status'
    verification_status.admin_order_field = 'is_verified'
    
    def document_links(self, obj):
        """Display links to uploaded documents"""
        links = []
        if obj.certificate_of_practice:
            links.append(
                format_html(
                    '<a href="{}" target="_blank">📄 Certificate of Practice</a>',
                    obj.certificate_of_practice.url
                )
            )
        if obj.id_document:
            links.append(
                format_html(
                    '<a href="{}" target="_blank">🆔 ID Document</a>',
                    obj.id_document.url
                )
            )
        if not links:
            return format_html('<span style="color: gray;">No documents uploaded</span>')
        return format_html('<br>'.join(links))
    document_links.short_description = 'Uploaded Documents'
    
    def verify_experts(self, request, queryset):
        """Admin action to verify selected experts"""
        updated = queryset.filter(account_type='expert').update(is_verified=True)
        self.message_user(
            request,
            f'Successfully verified {updated} expert(s).'
        )
    verify_experts.short_description = 'Verify selected experts'
    
    def unverify_experts(self, request, queryset):
        """Admin action to unverify selected experts"""
        updated = queryset.filter(account_type='expert').update(is_verified=False)
        self.message_user(
            request,
            f'Successfully unverified {updated} expert(s).'
        )
    unverify_experts.short_description = 'Unverify selected experts'
    
    def export_expert_list(self, request, queryset):
        """Admin action to export expert list (placeholder)"""
        experts = queryset.filter(account_type='expert')
        self.message_user(
            request,
            f'Export functionality for {experts.count()} experts would be implemented here.'
        )
    export_expert_list.short_description = 'Export expert list'

# Extend User Admin to include UserProfile
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = BaseUserAdmin.list_display + ('get_account_type', 'get_verification_status')
    list_filter = BaseUserAdmin.list_filter + ('profile__account_type', 'profile__is_verified')
    
    def get_account_type(self, obj):
        try:
            return obj.profile.get_account_type_display()
        except UserProfile.DoesNotExist:
            return 'No Profile'
    get_account_type.short_description = 'Account Type'
    get_account_type.admin_order_field = 'profile__account_type'
    
    def get_verification_status(self, obj):
        try:
            if obj.profile.is_expert:
                return '✓ Verified' if obj.profile.is_verified else '⏳ Pending'
            return 'N/A'
        except UserProfile.DoesNotExist:
            return 'No Profile'
    get_verification_status.short_description = 'Verification'
    get_verification_status.admin_order_field = 'profile__is_verified'

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(FarmData)
class FarmDataAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'land_size', 'soil_type', 'fertilizer_type', 'water_access', 'created_at']
    list_filter = ['soil_type', 'fertilizer_type', 'water_access', 'created_at']
    search_fields = ['user__username', 'user__email', 'location']
    readonly_fields = ['created_at']

@admin.register(CropRecommendation)
class CropRecommendationAdmin(admin.ModelAdmin):
    list_display = ['crop_name', 'farm_data', 'suitability_score', 'confidence_level', 'created_at']
    list_filter = ['confidence_level', 'created_at']
    search_fields = ['crop_name', 'farm_data__user__username', 'farm_data__location']
    readonly_fields = ['created_at']

@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'content']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(ExpertConsultation)
class ExpertConsultationAdmin(admin.ModelAdmin):
    list_display = ['subject', 'customer', 'expert', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['subject', 'description', 'customer__username', 'expert__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Consultation Details', {
            'fields': ('customer', 'expert', 'subject', 'description')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_pending', 'mark_as_accepted', 'mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'Marked {updated} consultation(s) as pending.')
    mark_as_pending.short_description = 'Mark as pending'
    
    def mark_as_accepted(self, request, queryset):
        updated = queryset.update(status='accepted')
        self.message_user(request, f'Marked {updated} consultation(s) as accepted.')
    mark_as_accepted.short_description = 'Mark as accepted'
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'Marked {updated} consultation(s) as completed.')
    mark_as_completed.short_description = 'Mark as completed'
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'Marked {updated} consultation(s) as cancelled.')
    mark_as_cancelled.short_description = 'Mark as cancelled'
