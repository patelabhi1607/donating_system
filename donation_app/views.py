import stripe
import stripe.error
from django.contrib.auth import get_user_model, login
from django.db.models import Sum
from django.http import JsonResponse
from django_otp.models import Device
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from donation_app.models import Donation
from donation_app.serializers import DonationSerializer
from donation_system import settings

User = get_user_model()
stripe.api_key = settings.STRIPE_API_KEY


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()

    @action(detail=False, methods=["POST"])
    def login(self, request):
        phone_number = request.data.get("phone_number")
        otp = request.data.get("otp")

        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the default OTP device for the user
        default_device = Device.objects.get(user=user, name="default")
        if not default_device:
            return Response({"message": "No OTP device found"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the OTP token
        if not default_device.verify_token(otp):
            return Response({"message": "Invalid OTP"}, status=status.HTTP_401_UNAUTHORIZED)

        # Login the user
        login(request, user)

        return Response({"message": "Logged in successfully"})


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["POST"])
    def process_donation(self, request):
        amount = request.data.get("amount")

        # Create a charge using the Stripe payment gateway
        try:
            charge = stripe.Charge.create(  # noqa: ignore
                amount=int(amount * 100),  # Stripe accepts amounts in cents
                currency="usd",  # Set the appropriate currency code
                source=request.data.get("token"),  # Payment token received from client-side
                description="Donation",
                statement_descriptor="Donation",
            )

            # Save the donation in the database
            donation = Donation.objects.create(  # noqa: ignore
                user=self.request.user,
                amount=amount,
            )

            # Return success response
            return JsonResponse({"message": "Donation processed successfully"})

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get("error", {})
            return Response({"message": err.get("message")}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.RateLimitError:
            # Too many requests made to the API too quickly
            return Response({"message": "Too many requests"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        except stripe.error.InvalidRequestError:
            # Invalid parameters were supplied to Stripe's API
            return Response({"message": "Invalid parameters"}, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.AuthenticationError:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return Response({"message": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

        except stripe.error.APIConnectionError:
            # Network communication with Stripe failed
            return Response({"message": "Network error"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except stripe.error.StripeError:
            # Display a very generic error to the user
            return Response({"message": "Payment failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception:
            # Something else happened, completely unrelated to Stripe
            return Response({"message": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["GET"])
    def payment_history(self, request):
        user = self.request.user
        donations = Donation.objects.filter(user=user)
        serializer = DonationSerializer(donations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"])
    def monthly_payment_dashboard(self, request):
        user = self.request.user
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        donations = Donation.objects.filter(user=user, date__range=[start_date, end_date])
        total_amount = donations.aggregate(Sum("amount")).get("amount__sum", 0)
        serializer = DonationSerializer(donations, many=True)
        return Response({"data": serializer.data, "total_amount": total_amount})
