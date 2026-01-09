"""
API Authentication Views
PyService Mini-ITSM Platform

JWT token endpoints and 2FA verification.
"""

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
import pyotp
import qrcode
import base64
from io import BytesIO

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer with additional user data."""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.get_full_name()
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra response data
        data['user'] = {
            'id': self.user.pk,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
            'full_name': self.user.get_full_name(),
            'department': self.user.department.name if self.user.department else None,
        }
        
        # Check if 2FA is enabled
        data['requires_2fa'] = hasattr(self.user, 'two_factor_device') and self.user.two_factor_device.is_verified
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with additional user info."""
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """Logout by blacklisting the refresh token."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """Get current user profile."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'id': user.pk,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'role_display': user.get_role_display(),
            'department': {
                'id': user.department.pk,
                'name': user.department.name
            } if user.department else None,
            'phone': user.phone,
            'employee_id': user.employee_id,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
            'two_factor_enabled': hasattr(user, 'two_factor_device') and user.two_factor_device.is_verified,
        })
    
    def patch(self, request):
        user = request.user
        allowed_fields = ['first_name', 'last_name', 'phone', 'email']
        
        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
        
        user.save()
        return Response({'detail': 'Profile updated successfully.'})


class TwoFactorSetupView(APIView):
    """Setup 2FA for the user."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Generate 2FA secret and QR code."""
        user = request.user
        
        # Generate secret
        secret = pyotp.random_base32()
        
        # Create TOTP
        totp = pyotp.TOTP(secret)
        
        # Generate provisioning URI
        provisioning_uri = totp.provisioning_uri(
            name=user.email or user.username,
            issuer_name='PyService ITSM'
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Store secret temporarily (should be verified before saving permanently)
        request.session['temp_2fa_secret'] = secret
        
        return Response({
            'secret': secret,
            'qr_code': f'data:image/png;base64,{qr_code_base64}',
            'provisioning_uri': provisioning_uri,
        })
    
    def post(self, request):
        """Verify and enable 2FA."""
        user = request.user
        code = request.data.get('code')
        secret = request.session.get('temp_2fa_secret')
        
        if not secret:
            return Response(
                {'detail': 'Please generate a 2FA secret first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not code:
            return Response(
                {'detail': 'Verification code is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify the code
        totp = pyotp.TOTP(secret)
        if totp.verify(code):
            # Save the 2FA device
            TwoFactorDevice.objects.update_or_create(
                user=user,
                defaults={
                    'secret': secret,
                    'is_verified': True,
                }
            )
            
            # Clean up session
            del request.session['temp_2fa_secret']
            
            # Generate backup codes
            backup_codes = [pyotp.random_base32()[:8] for _ in range(10)]
            
            return Response({
                'detail': '2FA enabled successfully.',
                'backup_codes': backup_codes,
            })
        else:
            return Response(
                {'detail': 'Invalid verification code.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TwoFactorVerifyView(APIView):
    """Verify 2FA code during login."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        code = request.data.get('code')
        
        if not user_id or not code:
            return Response(
                {'detail': 'User ID and code are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(pk=user_id)
            device = user.two_factor_device
            
            totp = pyotp.TOTP(device.secret)
            if totp.verify(code):
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'detail': '2FA verification successful.',
                })
            else:
                return Response(
                    {'detail': 'Invalid 2FA code.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TwoFactorDisableView(APIView):
    """Disable 2FA for the user."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        password = request.data.get('password')
        
        if not password:
            return Response(
                {'detail': 'Password is required to disable 2FA.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.check_password(password):
            return Response(
                {'detail': 'Invalid password.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            device = user.two_factor_device
            device.delete()
            return Response({'detail': '2FA disabled successfully.'})
        except Exception:
            return Response(
                {'detail': '2FA is not enabled for this account.'},
                status=status.HTTP_400_BAD_REQUEST
            )


# Import model here to avoid circular imports
try:
    from cmdb.models import TwoFactorDevice
except ImportError:
    # Model will be created separately
    TwoFactorDevice = None
