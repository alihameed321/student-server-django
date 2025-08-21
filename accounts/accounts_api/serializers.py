from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, StudentProfile, StaffProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'university_id', 'user_type', 'phone_number', 'date_of_birth',
            'major', 'academic_level', 'enrollment_year', 'department', 'position'
        ]
        read_only_fields = ['id', 'username']


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for StudentProfile model"""
    
    class Meta:
        model = StudentProfile
        fields = [
            'student_id_number', 'gpa', 'total_credits', 'graduation_date',
            'emergency_contact_name', 'emergency_contact_phone'
        ]


class StaffProfileSerializer(serializers.ModelSerializer):
    """Serializer for StaffProfile model"""
    
    class Meta:
        model = StaffProfile
        fields = [
            'employee_id', 'hire_date', 'permissions'
        ]


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')
        
        if identifier and password:
            # Try to authenticate with username first
            user = authenticate(username=identifier, password=password)
            
            # If username authentication fails, try with email
            if not user:
                try:
                    user_obj = User.objects.get(email=identifier)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            # If email authentication fails, try with university_id
            if not user:
                try:
                    user_obj = User.objects.get(university_id=identifier)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include identifier and password')


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for authenticated user"""
    student_profile = StudentProfileSerializer(read_only=True)
    staff_profile = StaffProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'university_id', 'user_type', 'phone_number', 'date_of_birth',
            'major', 'academic_level', 'enrollment_year', 'department', 'position',
            'is_student', 'is_staff_member', 'student_profile', 'staff_profile'
        ]
        read_only_fields = ['id', 'username', 'is_student', 'is_staff_member']