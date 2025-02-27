from django.urls import path
from .views import RegisterView, LoginView, AllUserView, SendEmail
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # path('register/', RegisterView.as_view()),
    # path('login/', TokenObtainPairView.as_view()),
    # path('admin/', TokenRefreshView.as_view()),
    # path('admin/dashboard', AdminView.as_view()),
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('views/', AllUserView.as_view()),
    path('email/', SendEmail.as_view())
]