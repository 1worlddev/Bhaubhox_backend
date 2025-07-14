from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, OrderSerializer, UserProfileSerializer, DogSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from .models import Order
from datetime import date
from . serializers import *
from django.contrib.auth import get_user_model

from rest_framework.parsers import MultiPartParser, FormParser

from rest_framework_simplejwt.views import TokenObtainPairView



class SignupWithDogView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()

            user_email = result["user"]["email"]
            user_name = user_email.split("@")[0].capitalize()

            html_content = f"""
                <div style="font-family:Arial,sans-serif;padding:20px;background:#f9f9f9;">
                    <h2 style="color:#4CAF50;">Welcome to BarkBox, {user_name}!</h2>
                    <p>Thanks for signing up. We’re excited to send goodies your dog will love 🐶</p>
                    <p>Explore your dashboard and update your preferences anytime.</p>
                    <p style="margin-top:30px;">Cheers,<br/>The BarkBox Team</p>
                </div>
            """

            try:
                email = EmailMessage(
                    subject="🎉 Welcome to BarkBox!",
                    body=html_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user_email],
                )
                email.content_subtype = "html"
                email.send()
            except Exception as e:
                print(f"❌ Failed to send welcome email: {e}")

            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile
from .serializers import UserShippingSerializer

class UserShippingInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserShippingSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserShippingSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from .serializers import UserProfileDetailSerializer

class UserFullProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileDetailSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileDetailSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateAccountInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        latest_order = Order.objects.filter(user=user).order_by('-created_at').first()

        user_serializer = UserProfileSerializer(user, data=request.data, partial=True)
        order_serializer = None

        if latest_order:
            order_serializer = UserAddressSerializer(latest_order, data=request.data, partial=True)

        if user_serializer.is_valid() and (not latest_order or order_serializer.is_valid()):
            user_serializer.save()
            if order_serializer:
                order_serializer.save()
            return Response({'message': 'Account info updated'}, status=200)

        errors = {}
        errors.update(user_serializer.errors)
        if order_serializer:
            errors.update(order_serializer.errors)
        return Response(errors, status=400)


from datetime import timedelta
from dateutil.relativedelta import relativedelta 
User = get_user_model()

from dateutil.relativedelta import relativedelta


from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order
from .serializers import OrderBoxHistorySerializer

# class UserBoxHistoryView(APIView):
    # permission_classes = [IsAuthenticated]

    # def get(self, request):
    #     orders = Order.objects.filter(user=request.user).select_related("monthly_box").order_by("-created_at")
    #     serializer = OrderBoxHistorySerializer(orders, many=True)
    #     return Response(serializer.data)



# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import api_view, permission_classes
# from .models import Order
# from .serializers import OrderRatingSerializer

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def rate_box(request, box_id):
#     try:
#         order = Order.objects.get(id=box_id, user=request.user)
#     except Order.DoesNotExist:
#         return Response({'error': 'Order not found.'}, status=404)

#     serializer = OrderRatingSerializer(order, data=request.data, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         return Response({'message': 'Rating updated.'})
#     return Response(serializer.errors, status=400)



# class RateBoxView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, order_id):
#         try:
#             order = Order.objects.get(id=order_id, user=request.user)
#             box = order.monthly_box
#             if not box:
#                 return Response({"error": "Box not found for this order."}, status=404)

#             rating = request.data.get('rating')
#             if not isinstance(rating, int) or not (1 <= rating <= 5):
#                 return Response({"error": "Rating must be an integer between 1 and 5."}, status=400)

#             # ✅ Update order's rating
#             order.rating = rating
#             order.save()

#             # ✅ Recalculate MonthlyBox rating from all linked orders
#             related_orders = box.orders.exclude(rating=0)
#             total_ratings = related_orders.count()
#             rating_sum = sum(o.rating for o in related_orders)
#             box.rating = round(rating_sum / total_ratings, 1)
#             box.total_ratings = total_ratings
#             box.rating_sum = rating_sum
#             box.save()

#             return Response({"message": "Thanks for rating!"}, status=200)

#         except Order.DoesNotExist:
#             return Response({"error": "Order not found or not yours."}, status=404)






from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer
from datetime import timedelta


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, OrderSerializer, UserProfileSerializer, DogSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from .models import Order
from datetime import date
from django.contrib.auth import get_user_model




class SignupWithDogView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()

            user_email = result["user"]["email"]
            user_name = user_email.split("@")[0].capitalize()

            html_content = f"""
                <div style="font-family:Arial,sans-serif;padding:20px;background:#f9f9f9;">
                    <h2 style="color:#4CAF50;">Welcome to BarkBox, {user_name}!</h2>
                    <p>Thanks for signing up. We’re excited to send goodies your dog will love 🐶</p>
                    <p>Explore your dashboard and update your preferences anytime.</p>
                    <p style="margin-top:30px;">Cheers,<br/>The BarkBox Team</p>
                </div>
            """

            try:
                email = EmailMessage(
                    subject="🎉 Welcome to BarkBox!",
                    body=html_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user_email],
                )
                email.content_subtype = "html"
                email.send()
            except Exception as e:
                print(f"❌ Failed to send welcome email: {e}")

            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from datetime import timedelta
from dateutil.relativedelta import relativedelta 
User = get_user_model()

# class OrderCheckoutView(APIView):
#     def post(self, request):
#         from .models import MonthlyBox
#         serializer = OrderSerializer(data=request.data)
#         if serializer.is_valid():
#             user = User.objects.filter(email=serializer.validated_data['email']).first()
#             if not user:
#                 return Response({'error': 'User not found'}, status=404)

#             # First box date logic (1 month after signup)
#             first_box_date = user.date_joined.date() + relativedelta(months=1)
#             today = date.today()

#             try:
#                 box = MonthlyBox.objects.get(month=today.month, year=today.year)
#             except MonthlyBox.DoesNotExist:
#                 return Response({'error': 'No MonthlyBox defined for this month'}, status=400)

#             order = serializer.save()
#             order.monthly_box = box
#             order.total_treats_delivered = 2
#             order.total_toys_delivered = 3
#             order.created_at = first_box_date  # delay order creation to match first delivery logic
#             order.save()

#             return Response({'order_id': order.id, 'message': 'Order placed successfully'}, status=201)

#         return Response(serializer.errors, status=400)



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DogProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        dog = getattr(request.user, "dog", None)
        if dog:
            serializer = DogSerializer(dog)
            return Response(serializer.data)
        return Response({"detail": "Dog profile not found."}, status=404)

    def put(self, request):
        dog = getattr(request.user, "dog", None)
        if not dog:
            return Response({"detail": "Dog profile not found."}, status=404)
        serializer = DogSerializer(dog, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class SendEmailAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        to_email = request.data.get('to')
        subject = request.data.get('subject')
        html_content = request.data.get('html')

        print("📩 Email Request Received:")
        print("To:", to_email)
        print("Subject:", subject)
        print("HTML snippet:", html_content[:100])

        if not all([to_email, subject, html_content]):
            return Response({'error': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            email = EmailMessage(
                subject,
                html_content,
                settings.DEFAULT_FROM_EMAIL,
                [to_email],
            )
            email.content_subtype = "html"
            email.send()
            return Response({'message': 'Email sent'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from dateutil.relativedelta import relativedelta


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import Order, MonthlyBox
from .serializers import OrderSerializer
from django.contrib.auth.models import User

class OrderCheckoutView(APIView):
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.filter(email=serializer.validated_data['email']).first()
            if not user:
                return Response({'error': 'User not found'}, status=404)

            # First box date = 1 month after signup
            first_box_date = user.date_joined.date() + relativedelta(months=1)

            # Get box of that future month
            try:
                box = MonthlyBox.objects.get(month=first_box_date.month, year=first_box_date.year)
            except MonthlyBox.DoesNotExist:
                return Response({'error': 'No MonthlyBox defined for first delivery month'}, status=400)

            order = serializer.save()
            order.user = user
            order.monthly_box = box
            order.total_treats_delivered = 2
            order.total_toys_delivered = 3
            order.created_at = first_box_date
            order.save()

            return Response({'order_id': order.id, 'message': 'Order placed successfully'}, status=201)

        return Response(serializer.errors, status=400)




class UpdateOrderStatusView(APIView):
    def post(self, request, order_id):
        new_status = request.data.get("status")
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id)
            order.status = new_status

            if new_status == 'delivered':
                # ✅ Only update if not already processed
                if order.total_treats_delivered < 2 and order.total_toys_delivered < 3:
                    # Update current order
                    order.total_treats_delivered += 2
                    order.total_toys_delivered += 3
                    order.save()

                    # Schedule next month's order
                    next_date = order.created_at.date() + relativedelta(months=1)
                    try:
                        next_box = MonthlyBox.objects.get(month=next_date.month, year=next_date.year)
                    except MonthlyBox.DoesNotExist:
                        next_box = None

                    # ✅ Prevent duplicate future order
                    duplicate = Order.objects.filter(
                        user=order.user,
                        monthly_box=next_box,
                        status__in=['confirmed', 'processing', 'shipped', 'out_for_delivery', 'delivered']
                    ).exists()

                    if not duplicate:
                        Order.objects.create(
                            user=order.user,
                            billing_type=order.billing_type,
                            selected_plan=order.selected_plan,
                            first_name=order.first_name,
                            last_name=order.last_name,
                            email=order.email,
                            address=order.address,
                            city=order.city,
                            state=order.state,
                            zip=order.zip,
                            use_shipping_as_billing=order.use_shipping_as_billing,
                            payment_method=order.payment_method,
                            status='confirmed',
                            monthly_box=next_box,
                            total_treats_delivered=0,
                            total_toys_delivered=0,
                            created_at=next_date,
                        )
                    else:
                        print("🛑 Skipping duplicate future order.")
                else:
                    print("🛑 Order already marked delivered previously.")
            else:
                # ✅ For all other statuses: just save
                order.save()

            return Response({"message": f"Order status updated to {new_status}"}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)


from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from main.models import MonthlyBox, Order, UserProfile
from .serializers import OrderSerializer


class DirectSubscriptionCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extract plan and payment data sent by frontend
        plan_data = {
            "selected_plan": request.data.get("selected_plan"),
            "billing_type": request.data.get("billing_type"),
            "payment_method": request.data.get("payment_method"),
            "use_shipping_as_billing": request.data.get("use_shipping_as_billing", True),
        }

        # Fetch user profile and dog profile info from DB for authenticated user
        user_profile = UserProfile.objects.filter(user=request.user).first()
        user_profile = UserProfile.objects.get(user=user)
        dog_profile = getattr(request.user, 'dog', None)

        if not user_profile:
            return Response({"error": "User profile not found."}, status=400)

        # Combine all data for serializer
        combined_data = {
            **plan_data,
            "email": request.user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user_profile.phone,
            "address": user_profile.address,
            "city": user_profile.city,
            "state": user_profile.state,
            "zip": user_profile.zip,
            # Agar dog profile fields serializer mein chahiye to yahan add karo
        }

        serializer = OrderSerializer(data=combined_data)
        if serializer.is_valid():
            user = request.user
            # Set first delivery box date 1 month after user signup
            first_box_date = user.date_joined.date() + relativedelta(months=1)

            try:
                box = MonthlyBox.objects.get(month=first_box_date.month, year=first_box_date.year)
            except MonthlyBox.DoesNotExist:
                return Response({'error': 'No MonthlyBox defined for first delivery month'}, status=400)

            order = serializer.save(user=user)
            order.monthly_box = box
            order.total_treats_delivered = 2
            order.total_toys_delivered = 3
            order.created_at = first_box_date
            order.save()

            return Response({'order_id': order.id, 'message': 'Direct subscription placed successfully'}, status=201)

        return Response(serializer.errors, status=400)




from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order
from .serializers import OrderBoxHistorySerializer


from collections import OrderedDict
from .serializers import OrderBoxHistorySerializer

class UserBoxHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).select_related("monthly_box").order_by("-created_at")

        # ✅ Pick only latest per month-year combo
        unique_orders = OrderedDict()
        for order in orders:
            key = (order.created_at.month, order.created_at.year)
            if key not in unique_orders:
                unique_orders[key] = order  # Pick only latest per month

        serializer = OrderBoxHistorySerializer(list(unique_orders.values()), many=True)
        return Response(serializer.data)



from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .models import Order
from .serializers import OrderRatingSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_box(request, box_id):
    try:
        order = Order.objects.get(id=box_id, user=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found.'}, status=404)

    serializer = OrderRatingSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Rating updated.'})
    return Response(serializer.errors, status=400)



class RateBoxView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            box = order.monthly_box
            if not box:
                return Response({"error": "Box not found for this order."}, status=404)

            rating = request.data.get('rating')
            if not isinstance(rating, int) or not (1 <= rating <= 5):
                return Response({"error": "Rating must be an integer between 1 and 5."}, status=400)

            # ✅ Update order's rating
            order.rating = rating
            order.save()

            # ✅ Recalculate MonthlyBox rating from all linked orders
            related_orders = box.orders.exclude(rating=0)
            total_ratings = related_orders.count()
            rating_sum = sum(o.rating for o in related_orders)
            box.rating = round(rating_sum / total_ratings, 1)
            box.total_ratings = total_ratings
            box.rating_sum = rating_sum
            box.save()

            return Response({"message": "Thanks for rating!"}, status=200)

        except Order.DoesNotExist:
            return Response({"error": "Order not found or not yours."}, status=404)






from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer
from datetime import timedelta

from calendar import month_name
from datetime import timedelta, date
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order, MonthlyBox
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order, MonthlyBox
from dateutil.relativedelta import relativedelta
from datetime import timedelta


from collections import OrderedDict
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order, MonthlyBox

class CurrentSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        order = Order.objects.filter(user=user).order_by('created_at').first()
        if not order:
            return Response({'detail': 'No subscription found'}, status=404)

        # Plan duration (e.g. "3 Month" → 3)
        import re
        match = re.search(r'\d+', order.selected_plan)
        # plan_duration = int(match.group()) if match else 1
        raw_duration = int(match.group()) if match else 1
        plan_duration = raw_duration  # don't subtract skipped_months here

        # Start date of subscription
        start_date = order.created_at.date()

        # All confirmed or delivered orders grouped by (month, year)
        orders = Order.objects.filter(user=user, status__in=['delivered', 'confirmed']).order_by('-created_at')
        unique_orders = OrderedDict()
        for o in orders:
            key = (o.created_at.month, o.created_at.year)
            if key not in unique_orders:
                unique_orders[key] = o

        delivered_count = len(unique_orders)
        skipped = order.skipped_months

        # Next delivery date
        next_delivery_date = start_date + relativedelta(months=delivered_count + skipped + 1)
        

        # Next billing = fixed from original start date + plan duration
        next_billing = start_date + relativedelta(months=plan_duration)
        ship_date = next_delivery_date - timedelta(days=5)

        # Remaining = plan - delivered
        # remaining_months = max(plan_duration - delivered_count, 0)
        remaining_months = max(plan_duration - delivered_count, 0)
        

        # Boxes
        current_box = MonthlyBox.objects.filter(month=order.created_at.month, year=order.created_at.year).first()
        next_box = MonthlyBox.objects.filter(month=next_delivery_date.month, year=next_delivery_date.year).first()

        # Accurate treat/toy delivered counts from *delivered* boxes only
        total_treats_delivered = sum(
            o.total_treats_delivered for o in unique_orders.values() if o.status == 'delivered'
        )
        total_toys_delivered = sum(
            o.total_toys_delivered for o in unique_orders.values() if o.status == 'delivered'
        )

        return Response({
            "plan": order.get_selected_plan_display(),
            "remaining_months": remaining_months,
            "next_billing": next_billing.strftime("%B %d, %Y"),
            "ship_date": ship_date.strftime("%B %d"),
            "dog_size": user.dog.get_size_display() if hasattr(user, 'dog') else "N/A",
            "total_boxes_delivered": delivered_count,
            "total_treats_delivered": total_treats_delivered,
            "total_toys_delivered": total_toys_delivered,
            "next_box": {
                "theme": next_box.name if next_box else None,
                "image": next_box.image_public_url if next_box else None
            } if next_box else None,
            "current_box": {
                "theme": current_box.name if current_box else None,
                "image": current_box.image_public_url if current_box else None
            } if current_box else None
        })


# class CurrentSubscriptionView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         order = Order.objects.filter(user=user).order_by('created_at').first()
#         if not order:
#             return Response({'detail': 'No subscription found'}, status=404)

#         # Plan duration from string like "3 Month"
#         import re
#         match = re.search(r'\d+', order.selected_plan)
#         plan_duration = int(match.group()) if match else 1

#         # Start date = first order date (1st delivery)
#         start_date = order.created_at.date()

#         # Next delivery = start + (delivered + skipped + 1 months)
#         # delivered_count = Order.objects.filter(user=user, status='delivered').count()
#         delivered_count = Order.objects.filter(user=request.user, status__in=['delivered', 'confirmed']).count()

#         skipped = order.skipped_months
#         next_delivery_date = start_date + relativedelta(months=delivered_count + skipped + 1)

#         # Fixed billing date = start + plan months
#         next_billing = start_date + relativedelta(months=plan_duration)
#         ship_date = next_delivery_date - timedelta(days=5)

#         # Remaining = plan - delivered
#         remaining_months = max(plan_duration - delivered_count, 0)

#         # Boxes
#         current_box = MonthlyBox.objects.filter(month=order.created_at.month, year=order.created_at.year).first()
#         next_box = MonthlyBox.objects.filter(month=next_delivery_date.month, year=next_delivery_date.year).first()

#         total_treats_delivered = sum(o.total_treats_delivered for o in Order.objects.filter(user=user, status='delivered'))
#         total_toys_delivered = sum(o.total_toys_delivered for o in Order.objects.filter(user=user, status='delivered'))

#         return Response({
#             "plan": order.get_selected_plan_display(),
#             "remaining_months": remaining_months,
#             "next_billing": next_billing.strftime("%B %d, %Y"),
#             "ship_date": ship_date.strftime("%B %d"),
#             "dog_size": user.dog.get_size_display() if hasattr(user, 'dog') else "N/A",
#             "total_boxes_delivered": delivered_count,
#             "total_treats_delivered": total_treats_delivered,
#             "total_toys_delivered": total_toys_delivered,
#             "next_box": {
#                 "theme": next_box.name if next_box else None,
#                 "image": next_box.image_public_url if next_box else None
#             } if next_box else None,
#             "current_box": {
#                 "theme": current_box.name if current_box else None,
#                 "image": current_box.image_public_url if current_box else None
#             } if current_box else None
#         })




class PauseSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        active_order = Order.objects.filter(user=user, status__in=['confirmed', 'processing', 'shipped', 'out_for_delivery']).first()
        if not active_order:
            return Response({'error': 'No active subscription found'}, status=404)

        active_order.status = 'paused'
        active_order.save()

        return Response({'message': 'Subscription paused successfully'}, status=200)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order
from rest_framework import status

class SkipBoxView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order = Order.objects.filter(user=request.user).first()
        
        if not order:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        # Increment skipped months
        order.skipped_months += 1
        
        order.save()

        # Calculate remaining months based on selected plan and skipped months
        plan_duration = int(order.selected_plan[:2])  # e.g., '6mo' -> 6
        remaining_months = plan_duration + order.skipped_months  # Add skipped months
        
        # Update plan duration dynamically (e.g., 6 months becomes 7 after skipping)
        # order.selected_plan = f"{remaining_months}mo"
        order.skipped_months += 1
        order.save()

        # Return response with updated remaining months
        return Response({
            "message": "Next box skipped successfully.",
            "remaining_months": remaining_months  # Show updated remaining months after skip
        }, status=status.HTTP_200_OK)


import stripe
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def create_checkout_session(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'BhauBox 6 Month Subscription',
                        },
                        'unit_amount': int(44000 * 100 / 280),  # ≈ USD
                    },
                    'quantity': 1,
                },
            ],
            success_url='http://localhost:3000/success',
            cancel_url='http://localhost:3000/cancel',
        )
        return JsonResponse({'url': session.url})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
