from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework.exceptions import AuthenticationFailed
from .models import User
import jwt, datetime

# class RegisterView(generics.CreateAPIView):
#     serializer_class = UserSerializer
#     permission_classes = [permissions.AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         refresh = RefreshToken.for_user(user)
#         return Response({
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#         })

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