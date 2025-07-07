from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from .decorators import admin_required, administrator_required
from django.contrib.auth import logout


# from .models import Profile

User = get_user_model()


@api_view(['GET'])
def get_data(request):
    data = {
        "message": "Hello from Django!"
    }
    return Response(data)

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if user is not None:
        # Generate or get an existing token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        # Return the token to the frontend
        return Response({"token": token.key, "message": "Login successful"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logged out successfully"}, status=200)

@login_required
def dashboard_view(request):
    # Only logged in users can access this view
    return JsonResponse({"message": "This is the dashboard"})


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profil_view(request):
    user = request.user  # The authenticated user

    if request.method == 'GET':
        # Return user profile data
        return Response({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'username': user.username,
            'role': user.role  
        })
    
    if request.method == 'PATCH':
        # Update user profile data
        data = request.data
        
        # Update only the fields provided in the request
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        if 'username' in data:
            user.username = data['username']
        
        # Save the updated user information
        user.save()
        
        return Response({
            'message': 'Profile updated successfully'
        }, status=status.HTTP_200_OK)

@api_view(['POST'])
def get_security_question(request):
    username = request.data.get('username')

    # Try to fetch the user by username
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # If user is found, return the security question from the User model
    return Response({'security_question': user.security_question}, status=status.HTTP_200_OK)

@api_view(['POST'])
def verify_security_answer(request):
    username = request.data.get('username')
    security_answer = request.data.get('security_answer')
    new_password = request.data.get('new_password')

    # Fetch user based on the provided username
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the provided security answer matches (case-insensitive)
    if user.security_answer.lower() == security_answer.lower():
        # If the answer is correct, set the new password
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Incorrect security answer'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    # Check if the old password is correct
    if not user.check_password(old_password):
        return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

    # Set the new password
    user.set_password(new_password)
    user.save()

    return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)

# View to return CSRF token
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': request.META.get('CSRF_COOKIE')})

@api_view(['GET'])
@login_required
def get_sidebar_role(request):
    user = request.user
    role = user.role

    menu_items = {
        'Admin Sistem': {
            'homepage': '/daftar-akun',
            'menu': ['profil', 'daftar-akun', 'buat-akun']
        },
        'Pengendali Mutu': {
            'homepage': '/tracker-survei',
            'menu': ['profil', 'tracker-survei']
        },
        'Logistik': {
            'homepage': '/dashboard',
            'menu': ['dashboard', 'profil', 'tracker-survei', 'souvenir']
        },
        'Administrasi': {
            'homepage': '/dashboard',
            'menu': [
                'dashboard',
                'profil', 'list-klien', 
                'survei', 'tracker-survei',
                'generator-dokumen', 'daftar-dokumen'
            ]
        },
        'Eksekutif': {
            'homepage': '/dashboard',
            'menu': [
                'dashboard',
                'profil', 'list-klien', 
                'tracker-survei', 'survei', 'daftar-dokumen', 'generator-dokumen'
            ]
        }
    }

    if role in menu_items:
        return JsonResponse({
            'role': role,
            'homepage': menu_items[role]['homepage'],
            'menu': menu_items[role]['menu']
        })
    
    return JsonResponse({'error': 'Invalid role'}, status=403)

@api_view(['GET'])
@login_required
def check_role_eksekutif(request):
    user = request.user
    print(user.role)
    if user.role == 'Eksekutif':  
        return JsonResponse({'role': user.role})
    return JsonResponse({'error': 'Unauthorized'}, status=403)

@api_view(['GET'])
@login_required
def check_role_administrasi(request):
    user = request.user
    print(user.role)
    if user.role == 'Administrasi':  
        return JsonResponse({'role': user.role})
    return JsonResponse({'error': 'Unauthorized'}, status=403)

@api_view(['GET'])
@login_required
def check_role_logistik(request):
    user = request.user
    print(user.role)
    if user.role == 'Logistik':  
        return JsonResponse({'role': user.role})
    return JsonResponse({'error': 'Unauthorized'}, status=403)


@api_view(['GET'])
@login_required
def check_role_pengendalimutu(request):
    user = request.user
    print(user.role)
    if user.role == 'Pengendali Mutu':  
        return JsonResponse({'role': user.role})
    return JsonResponse({'error': 'Unauthorized'}, status=403)

@api_view(['GET'])
@login_required
def check_role_admin(request):
    user = request.user
    print(user.role)
    if user.role == 'Admin Sistem':  
        return JsonResponse({'role': user.role})
    return JsonResponse({'error': 'Unauthorized'}, status=403)

@api_view(['GET'])
@login_required
def check_role_proposal(request):
    user = request.user
    print(user.role)
    if user.role == 'Administrasi':  
        return JsonResponse({'role': user.role})
    elif user.role == 'Eksekutif':
        return JsonResponse({'role': user.role})
    return JsonResponse({'error': 'Unauthorized'}, status=403)

@api_view(['GET'])
@login_required
def check_role_dashboard(request):
    user = request.user
    if user.role:
        return JsonResponse({'role': user.role})
    return JsonResponse({'error': 'Unauthorized'}, status=403)