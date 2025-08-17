from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, StudentProfile, StaffProfile


class CustomUserAdmin(UserAdmin):
    """Custom admin for User model with university branding"""
    
    list_display = ('university_id', 'username', 'get_full_name', 'user_type', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff', 'date_joined', 'academic_level', 'department')
    search_fields = ('university_id', 'username', 'first_name', 'last_name', 'email')
    ordering = ('university_id',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'profile_picture'),
            'classes': ('collapse',)
        }),
        ('University info', {
            'fields': ('university_id', 'user_type', 'major', 'academic_level', 'enrollment_year', 'department', 'position'),
            'classes': ('wide',)
        }),
        ('Digital ID', {
            'fields': ('qr_code',),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'university_id', 'user_type', 'password1', 'password2'),
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name() or '-'
    get_full_name.short_description = 'Full Name'
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Admin for Student Profile"""
    list_display = ('user', 'student_id_number', 'gpa', 'total_credits', 'graduation_date')
    list_filter = ('graduation_date', 'gpa')
    search_fields = ('user__university_id', 'user__first_name', 'user__last_name', 'student_id_number')
    ordering = ('user__university_id',)
    
    fieldsets = (
        ('Student Information', {
            'fields': ('user', 'student_id_number'),
            'classes': ('wide',)
        }),
        ('Academic Details', {
            'fields': ('gpa', 'total_credits', 'graduation_date'),
            'classes': ('wide',)
        }),
    )


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    """Admin for Staff Profile"""
    list_display = ('user', 'employee_id', 'hire_date', 'salary')
    list_filter = ('hire_date',)
    search_fields = ('user__university_id', 'user__first_name', 'user__last_name', 'employee_id')
    ordering = ('user__university_id',)
    
    fieldsets = (
        ('Staff Information', {
            'fields': ('user', 'employee_id', 'hire_date'),
            'classes': ('wide',)
        }),
        ('Employment Details', {
            'fields': ('salary', 'permissions'),
            'classes': ('wide',)
        }),
    )


# Register the custom User admin
admin.site.register(User, CustomUserAdmin)

# Customize admin site headers and titles
admin.site.site_header = 'University Services Administration'
admin.site.site_title = 'University Admin'
admin.site.index_title = 'Welcome to University Services Administration'
