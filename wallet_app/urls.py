from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', views.register),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('fund/', views.fund),
    path('pay/', views.pay),
    path('balance/', views.balance),
    path('transactions/', views.transactions),
    path('add-product/', views.add_product),
    path('buy/', views.buy_product),
]
