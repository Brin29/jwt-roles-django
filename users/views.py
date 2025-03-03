from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from django.template.loader import get_template
from django.conf import settings
from rest_framework.response import Response
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import update_session_auth_hash
from rest_framework.exceptions import AuthenticationFailed
from datetime import timedelta
from django.utils import timezone
from .models import User
import jwt, datetime
import secrets
import string

class RegisterView(APIView):

    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):

        # para tomar al usuario segun el email
        email = request.data['email']
        # Tomar datos de la request para validarlos
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        # Validacion de datos
        if user is None:
            raise AuthenticationFailed('User not Found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect Password!')
        
        if user.is_temp_password:
            expiration_date = user.temp_password_date + timedelta(minutes=3)

            if timezone.now() > expiration_date:
                user.is_active = False
                user.save()
                raise AuthenticationFailed('Tu contraseña temporal ha expirado. Contacta al administrador.')

            return Response({
                'message': 'Debes cambiar tu contraseña temporal.'
            })

        payload = {
            'id': user.id,
            'exp': datetime.datetime.now() + datetime.timedelta(hours=60),
            'iat': datetime.datetime.now()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        
        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)

        response.data = {
            'jwt': token
        }

        return response


class AllUserView(APIView):
    def get(self, request):

        authenticate_user(request, role='ADMIN')

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class AdminView(APIView):
  def get(self, request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

class SendEmail(APIView):
    def post(self, request):

        # user = authenticate_user(request, role='ADMIN')
        
        # Generar contraseña temporal
        temp_password = generate_temp_password()
        request.data['password'] =  temp_password

        # Enviar data a la base de datos
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Actualizar contraseña temporal
        user.set_password(temp_password)
        user.is_temp_password = True
        user.temp_password_date = timezone.now()
        user.save()

        # tomar datos de la request
        email = request.data['email']
        username = request.data['username']
        role = request.data['role']

        # datos de respuesta al correo
        mail = create_email(
            email,
            'Enlace de ingreso',
            'autorizacion.html',
            {
                'username': username,
                'email': email,
                'password': temp_password,
                'role': role,
            }
        )

        mail.send(fail_silently=False)

        return Response({
            'message': 'Work'
        })

class ChangePasswordView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated')
        
        user = User.objects.filter(id=payload['id']).first()

        if not user:
            raise AuthenticationFailed('User not found!')
        
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({
                'message': 'Nueva contraseña no proporcionada'
            }, status=400)
        
        user.set_password(new_password)
        user.is_temp_password = False

        user.save()
        update_session_auth_hash(request, user)

        return Response({'message': 'Contraseña cambiada exitosamente'})


# Funcion para autenticar
def authenticate_user(request, role):
    token = request.COOKIES.get('jwt')

    if not token:
        raise AuthenticationFailed('Unauthenticated!')
    
    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated')
    
    user = User.objects.filter(id=payload['id']).first()

    if not user:
        raise AuthenticationFailed('User not found!')
    
    if user.role != role:
        raise AuthenticationFailed('Permission denied!')
    
    return user
    

# Funcion para enviar un email
def create_email(user_email, subject, template_name, context):
    template = get_template(template_name)
    content = template.render(context)

    message = EmailMultiAlternatives(
        subject=subject,
        body='',
        from_email=settings.EMAIL_HOST_USER,
        to=[
            user_email
        ],
        cc=[]
    )

    message.attach_alternative(content, 'text/html')
    return message

def generate_temp_password():
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(secrets.choice(alphabet) for _ in range(12))