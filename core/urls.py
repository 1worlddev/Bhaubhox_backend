# """
# URL configuration for core project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.2/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# from django.contrib import admin
# from django.urls import path
# from main.views import * 
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('api/signup/', SignupWithDogView.as_view(), name='signup-with-dog'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('api/checkout/', OrderCheckoutView.as_view(), name='checkout'),
#     path('api/user/profile/', UserProfileView.as_view(), name='user-profile'),
#     path('api/dog/profile/', DogProfileView.as_view(), name='dog-profile'),
#     path('api/send-email/', SendEmailAPIView.as_view(), name='send-email'),
#     path('api/box-history/', UserBoxHistoryView.as_view(), name='box-history'),
#     path('api/skip-box/', SkipBoxView.as_view(), name='skip-box'),
#     path('api/rate-box/<int:box_id>/', rate_box),
#     path('api/current-subscription/', CurrentSubscriptionView.as_view()),


# ]

from django.contrib import admin
from django.urls import path
from main.views import * 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/signup/', SignupWithDogView.as_view(), name='signup-with-dog'),
    path('account/update/', UpdateAccountInfoView.as_view(), name='account-update'),
    path('api/user/shipping/', UserShippingInfoView.as_view(), name='user-shipping-info'),
    
    path('api/create-checkout-session/', create_checkout_session),



    # Orders & Subscriptions
    path('api/checkout/', OrderCheckoutView.as_view(), name='checkout'),
    path('api/skip-box/', SkipBoxView.as_view(), name='skip-box'),
    path('api/box-history/', UserBoxHistoryView.as_view(), name='box-history'),
    path('api/current-subscription/', CurrentSubscriptionView.as_view(), name='current-subscription'),
    path('api/orders/update-status/<int:order_id>/', UpdateOrderStatusView.as_view(), name='update-order-status'),
    path("api/pause-subscription/", PauseSubscriptionView.as_view(), name="pause-subscription"),
    path('api/direct-subscription-checkout/', DirectSubscriptionCheckoutView.as_view(), name='direct_subscription_checkout'),

    # Rating
    path('api/rate-box/<int:box_id>/', rate_box),
    path('api/rate-box-detail/<int:order_id>/', RateBoxView.as_view(), name='rate-box-detail'),

    # Profiles
    path('api/user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/dog/profile/', DogProfileView.as_view(), name='dog-profile'),
    path('api/user/profile-detail/', UserFullProfileView.as_view(), name='user-profile-detail'),

    # Email
    path('api/send-email/', SendEmailAPIView.as_view(), name='send-email'),
]
