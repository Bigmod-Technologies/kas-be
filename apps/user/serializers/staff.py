from gc import set_debug
import secrets
import string
from rest_framework import serializers
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from apps.user.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ["phone_number", "nid", "dob", "profile_picture"]
        extra_kwargs = {
            "phone_number": {"required": False},
            "nid": {"required": False},
            "dob": {"required": False},
        }

    def to_representation(self, instance):
        """Override to return full URL for profile_picture"""
        representation = super().to_representation(instance)
        if representation.get('profile_picture'):
            request = self.context.get('request')
            if request:
                representation['profile_picture'] = request.build_absolute_uri(representation['profile_picture'])
        return representation


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for Group model"""

    class Meta:
        model = Group
        fields = ["id", "name"]


class StaffSerializer(serializers.ModelSerializer):
    """Serializer for Staff with Profile"""

    profile = ProfileSerializer(required=False)
    groups = GroupSerializer(many=True, read_only=True)
    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password],
        help_text="If not provided, a random password will be generated",
    )
    generated_password = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "generated_password",
            "groups",
            "profile",
            "date_joined",
            "is_active",
        ]
        read_only_fields = ["id", "date_joined", "generated_password", "groups"]
        extra_kwargs = {
            "email": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "is_active": {"default": True},
        }

    def generate_random_password(self):
        """Generate a random secure password"""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        # Ensure at least one of each type
        password = (
            secrets.choice(string.ascii_lowercase)
            + secrets.choice(string.ascii_uppercase)
            + secrets.choice(string.digits)
            + secrets.choice(string.punctuation)
        )
        # Fill the rest randomly
        password += "".join(secrets.choice(alphabet) for _ in range(8))
        # Shuffle the password
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        return "".join(password_list)

    def create(self, validated_data):
        """Create staff with profile and assign to both Salesman and Delivery man groups"""
        profile_data = validated_data.pop("profile", {})
        password = validated_data.pop("password", None)
        generated_password = None

        # Generate random password if not provided
        if not password:
            generated_password = self.generate_random_password()
            password = generated_password

        # Create staff
        staff = User.objects.create_user(**validated_data)
        staff.set_password(password)
        staff.save()

        # Assign staff to both groups by default
        salesman_group, _ = Group.objects.get_or_create(name="Salesman")
        delivery_man_group, _ = Group.objects.get_or_create(name="Delivery man")
        staff.groups.add(salesman_group, delivery_man_group)

        # Create or update profile
        Profile.objects.update_or_create(user=staff, defaults=profile_data)

        # Store generated password for response
        if generated_password:
            staff.generated_password = generated_password

        return staff

    def update(self, instance, validated_data):
        """Update staff and profile"""
        profile_data = validated_data.pop("profile", {})
        password = validated_data.pop("password", None)

        # Update staff fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update password if provided
        if password:
            instance.set_password(password)

        instance.save()

        # Update profile
        if profile_data:
            Profile.objects.update_or_create(user=instance, defaults=profile_data)

        return instance

    def to_representation(self, instance):
        """Customize representation to include profile"""
        representation = super().to_representation(instance)
        
        # Add profile data
        if hasattr(instance, "profile"):
            profile_serializer = ProfileSerializer(instance.profile, context=self.context)
            representation["profile"] = profile_serializer.data
        else:
            representation["profile"] = None

        # Add generated password if it exists (only for create operations)
        if hasattr(instance, "generated_password") and instance.generated_password:
            representation["generated_password"] = instance.generated_password

        return representation

