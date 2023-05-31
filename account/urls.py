from django.urls import path
from .views import UserObtainTokenPairView, RegisterView, user_view, payment_view, subscribe_view, \
    site_user_view, subscription_model_view, unsubscribe_view
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('login/', UserObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('user/subscribe/', subscribe_view, name='subscribe'),
    path('user/unsubscribe/', unsubscribe_view, name='unsubscribe'),
    path('subscription_models/', subscription_model_view, name='subscription_models'),
    path('payments/', payment_view, name='payments'),
    path('user/', user_view),
    path('user/site_user', site_user_view)

]
