import secrets
import string
from rest_framework import serializers
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from apps.user.models import Profile
from apps.area.models import Area


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class ProfileSerializer(serializers.ModelSerializer):
    from apps.area.serializers import AreaSerializer

    profile_picture = serializers.ImageField(required=False)
    areas = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Area.objects.all(),
        required=False,
        help_text="List of area IDs to assign to the profile",
    )
    areas_display = AreaSerializer(source="areas", many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            "phone_number",
            "nid",
            "dob",
            "profile_picture",
            "areas",
            "areas_display",
            "sales_commission_in_percentage",
            "monthly_salary",
        ]
        extra_kwargs = {
            "phone_number": {"required": False},
            "nid": {"required": False},
            "dob": {"required": False},
            "sales_commission_in_percentage": {"required": False},
            "monthly_salary": {"required": False},
        }

    def to_representation(self, instance):
        """Override to return full URL for profile_picture and show areas details"""
        representation = super().to_representation(instance)
        if representation.get("profile_picture"):
            request = self.context.get("request")
            if request:
                representation["profile_picture"] = request.build_absolute_uri(
                    representation["profile_picture"]
                )
        
        # Use areas_display for output, remove areas (IDs) from representation
        if "areas_display" in representation:
            representation["areas"] = representation.pop("areas_display")

        return representation


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for Group model"""

    class Meta:
        model = Group
        fields = ["id", "name"]


class StaffSerializer(serializers.ModelSerializer):
    """Serializer for Staff with Profile"""

    profile = ProfileSerializer(required=False)
    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        required=False,
        help_text="List of group IDs to assign to the staff",
    )
    groups_display = GroupSerializer(source="groups", many=True, read_only=True)
    password = serializers.CharField(
        write_only=True,
        required=False,
        validators=[validate_password],
        help_text="If not provided, a random password will be generated",
    )


    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "groups",
            "groups_display",
            "profile",
            "date_joined",
            "is_active",
        ]
        read_only_fields = ["id", "date_joined", "groups_display"]
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
        """Create staff with profile and assign groups"""
        profile_data = validated_data.pop("profile", None)
        groups_data = validated_data.pop("groups", [])
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

        # Assign groups if provided
        if groups_data:
            staff.groups.set(groups_data)

        # Handle profile creation if profile data is provided
        if profile_data is not None and profile_data:
            # Handle areas in profile data (ManyToMany field) - must be popped before creating profile
            areas_data = profile_data.pop("areas", None)
            
            # Get or create profile (signal may have already created it)
            profile, created = Profile.objects.get_or_create(user=staff)
            
            # Update all fields from profile_data
            # The nested serializer should have already validated the data
            for key, value in profile_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            profile.save()

            # Assign areas if provided (ManyToMany must be set after profile is saved)
            if areas_data is not None:
                profile.areas.set(areas_data)
            
            # # Refresh from database to ensure all data is loaded
            # profile.refresh_from_db()


        return staff

    def update(self, instance, validated_data):
        """Update staff and profile"""
        profile_data = validated_data.pop("profile", None)
        groups_data = validated_data.pop("groups", None)
        password = validated_data.pop("password", None)

        # Update staff fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update password if provided
        if password:
            instance.set_password(password)

        instance.save()

        # Update groups if provided
        if groups_data is not None:
            instance.groups.set(groups_data)

        # Handle profile update if profile data is provided
        if profile_data is not None:
            # Handle areas in profile data (ManyToMany field)
            areas_data = profile_data.pop("areas", None)
            
            # Get or create profile
            profile, _ = Profile.objects.get_or_create(user=instance)
            
            # Update all fields from profile_data
            # Empty strings should be converted to None for nullable fields
            for key, value in profile_data.items():
                if value == "":
                    # Convert empty strings to None for nullable fields
                    setattr(profile, key, None)
                else:
                    setattr(profile, key, value)
            profile.save()

            # Update areas if provided
            if areas_data is not None:
                profile.areas.set(areas_data)

        return instance

    def to_representation(self, instance):
        """Customize representation to include profile"""
        representation = super().to_representation(instance)

        # Add profile data
        if hasattr(instance, "profile"):
            profile_serializer = ProfileSerializer(
                instance.profile, context=self.context
            )
            representation["profile"] = profile_serializer.data
        else:
            representation["profile"] = None


        # Use groups_display for output, remove groups (IDs) from representation
        if "groups_display" in representation:
            representation["groups"] = representation.pop("groups_display")

        return representation
