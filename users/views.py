from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from rest_framework.exceptions import AuthenticationFailed
from .permissions import IsAdmin, IsCliente
from .models import User
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication

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
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = RefreshToken.for_user(user)
        print(token)

        return Response({
            'jwt': str(token)
        })

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
        
        token = RefreshToken.for_user(user)
        print(user)

        # El token se guarda en una cookies
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': str(token)
        }

        return response


class AdminView(APIView):
    def get(self, request):
        JWT_authenticator = JWTAuthentication() 
        token = request.COOKIES.get('jwt')
        response_token = JWT_authenticator.authenticate(token)

        print(response_token)

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        return Response({ 
             "Message": "Acces"
        })



# class UserListView(generics.ListAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [IsAdmin]

# class EditorView(generics.RetrieveUpdateAPIView):
#     queryset = User.objects.filter(role='CLIENTE')
#     serializer_class = UserSerializer
#     permission_classes = [IsCliente]

# class AdminView(APIView):
#     # permission_classes = [permissions.AllowAny]
#     def get(self, request):

#         user = User.objects.filter(id=payload['id']).first()

#         return Response({
#             "message": "Hello World"
#         })