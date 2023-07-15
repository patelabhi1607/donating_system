from django.urls import include, path
from rest_framework import routers

from donation_app.views import DonationViewSet, UserViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"donations", DonationViewSet)


urlpatterns = [
    path("api/", include(router.urls)),
    path("api/users/login/", UserViewSet.as_view({"post": "login"}), name="user-login"),
    path("api/donations/process/", DonationViewSet.as_view({"post": "process_donation"}), name="donation-process"),
    path("api/donations/payment-history/", DonationViewSet.as_view({"get": "payment_history"}), name="payment-history"),
    path(
        "api/donations/monthly-payment-dashboard/",
        DonationViewSet.as_view({"get": "monthly_payment_dashboard"}),
        name="monthly-payment-dashboard",
    ),
]
