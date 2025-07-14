from rest_framework import serializers
from django.contrib.auth.models import User
from main.models import Dog
from rest_framework_simplejwt.tokens import RefreshToken


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.models import User

from .models import UserProfile

class UserShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['address', 'city', 'state', 'zip', 'phone']



class UserProfileDetailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)

    class Meta:
        model = UserProfile
        fields = ['email', 'first_name', 'last_name', 'phone', 'address', 'city', 'state', 'zip']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        for attr, value in user_data.items():
            
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class DogSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Dog
        exclude = ['owner']

    def get_image_url(self, obj):
        if obj.image:
            return obj.image_public_url
        return None

    def to_internal_value(self, data):
        data = data.copy()
        # ✅ Map incoming "dog_birth_date" to "adoptionDate"
        if "dog_birth_date" in data:
            data["adoptionDate"] = data.pop("dog_birth_date")
        return super().to_internal_value(data)


# class SignupSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True, min_length=6)
#     marketing_opt_in = serializers.BooleanField()
#     dog = DogSerializer()

#     def create(self, validated_data):
#         dog_data = validated_data.pop('dog')
#         user = User.objects.create_user(
#             username=validated_data['email'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )
#         Dog.objects.create(owner=user, **dog_data)
#         refresh = RefreshToken.for_user(user)
#         return {
#             "user": {
#                 "id": user.id,
#                 "email": user.email
#             },
#             "access": str(refresh.access_token),
#             "refresh": str(refresh),
#         }
class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)
    marketing_opt_in = serializers.BooleanField()

    dog_name = serializers.CharField()
    dog_gender = serializers.ChoiceField(choices=['boy', 'girl'])
    dog_size = serializers.ChoiceField(choices=['small', 'medium', 'large'])
    dog_allergies = serializers.CharField(required=False, allow_blank=True)
    dog_birth_date = serializers.CharField(required=False, allow_blank=True)
    dog_toy_preference = serializers.CharField(required=False, allow_blank=True)
    dog_breeds = serializers.CharField()  # will parse manually
    dog_photo = serializers.ImageField(required=False)

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data

    def create(self, validated_data):
        dog_data = {
            "name": validated_data.pop("dog_name"),
            "gender": validated_data.pop("dog_gender"),
            "size": validated_data.pop("dog_size"),
            "adoptionDate": validated_data.pop("dog_birth_date", ""),
            "image": validated_data.pop("dog_photo", None),
        }

        # Convert allergies to list
        allergies_string = validated_data.pop("dog_allergies", "")
        dog_data["allergies"] = [a.strip() for a in allergies_string.split(",") if a.strip() and a.upper() != "NONE"]

        # Convert comma-separated dog_breeds into list
        dog_breeds_raw = validated_data.pop("dog_breeds", "")
        dog_data["breeds"] = [b.strip() for b in dog_breeds_raw.split(",") if b.strip()]

        # Create user and dog
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"]
        )
        Dog.objects.create(owner=user, **dog_data)

        refresh = RefreshToken.for_user(user)
        return {
            "user": {
                "id": user.id,
                "email": user.email
            },
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


from rest_framework import serializers
from .models import Order

class SkipBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['skipped_months']

    def update(self, instance, validated_data):
        # Increment skipped months
        instance.skipped_months += 1
        # Adjust the selected plan
        current_plan_months = int(instance.selected_plan[:2])  # e.g., '6mo' => 6
        instance.selected_plan = f"{current_plan_months + instance.skipped_months}mo"
        instance.save()
        return instance




from rest_framework import serializers
from .models import Order
from django.contrib.auth.models import User

# class OrderSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(write_only=True)

#     class Meta:
#         model = Order
#         exclude = ['created_at', 'is_paid', 'user']  # we'll inject user manually

#     def create(self, validated_data):
#         email = validated_data.pop('email')
#         user = User.objects.filter(email=email).first()
#         if not user:
#             raise serializers.ValidationError({"user": ["No user found with this email."]})
#         validated_data['user'] = user
#         return Order.objects.create(**validated_data)

class OrderSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    sameAsBilling = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = Order
        exclude = ['created_at', 'is_paid', 'user']

    def create(self, validated_data):
        email = validated_data.pop('email')
        use_shipping_as_billing = validated_data.pop('sameAsBilling', True)  # fix name
        validated_data['use_shipping_as_billing'] = use_shipping_as_billing

        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError({"user": ["No user found with this email."]})
        validated_data['user'] = user
        return Order.objects.create(**validated_data)



from rest_framework import serializers
from .models import User, Dog

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['email', 'first_name', 'last_name', 'phone', 'address', 'city', 'state', 'zip']

# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = ['id', 'email', 'first_name', 'last_name', 'phone']  # ✅ Add 'phone'
#         extra_kwargs = {'email': {'read_only': True}}


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['address', 'city', 'state', 'zip']



class DogSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Dog
        exclude = ['owner']

    def get_image_url(self, obj):
        return obj.image_public_url





class OrderBoxHistorySerializer(serializers.ModelSerializer):
    box_name = serializers.CharField(source='monthly_box.name', read_only=True)
    box_theme = serializers.CharField(source='monthly_box.name', read_only=True)
    box_image_url = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'box_name', 'box_theme', 'box_image_url', 'month', 'year', 'status', 'rating']

    def get_box_image_url(self, obj):
        return obj.monthly_box.image_public_url if obj.monthly_box else None


    def get_month(self, obj):
        return obj.monthly_box.month if obj.monthly_box else None

    def get_year(self, obj):
        return obj.monthly_box.year if obj.monthly_box else None



class OrderRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['rating']
