from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, UserDetailSerializer
from ..models import User
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """API endpoint for mobile app login"""
    logger.info(f"Login attempt from IP: {request.META.get('REMOTE_ADDR')}")
    
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Log successful login
        logger.info(f"Successful login for user: {user.username} ({user.university_id})")
        
        # Prepare user data
        user_serializer = UserDetailSerializer(user)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)
    else:
        logger.warning(f"Failed login attempt from IP: {request.META.get('REMOTE_ADDR')}")
        return Response({
            'success': False,
            'message': 'Invalid credentials',
            'errors': serializer.errors
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """API endpoint for mobile app logout"""
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        logger.info(f"User logged out: {request.user.username}")
        return Response({
            'success': True,
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Logout error for user {request.user.username}: {str(e)}")
        return Response({
            'success': False,
            'message': 'Logout failed'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_user_profile(request):
    """API endpoint to get current user profile"""
    serializer = UserDetailSerializer(request.user)
    return Response({
        'success': True,
        'user': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_refresh_token(request):
    """API endpoint to refresh JWT token"""
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({
                'success': False,
                'message': 'Refresh token required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        access_token = token.access_token
        
        return Response({
            'success': True,
            'access_token': str(access_token)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Invalid refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)