from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from django.template.loader import get_template
from django.conf import settings
from rest_framework.response import Response
from django.core.mail import EmailMultiAlternatives
from rest_framework.exceptions import AuthenticationFailed
from .models import User
import jwt, datetime

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
        # serializer = UserSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()

        mail = create_email(
            'breinerstevendev@gmail.com',
            'Enlace de ingreso',
            'autorizacion.html',
            {
                'username': 'Breiner'
            }
        )

        mail.send(fail_silently=False)
        return Response({
            'message': 'Work'
        })

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