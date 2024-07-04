from rest_framework import serializers
from .models import TestModel, Profile
from django.contrib.auth import get_user_model

User = get_user_model()

class TestModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestModel
        fields = '__all__'


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'is_active', 'is_staff', 'last_login', 'date_joined', 'register_method')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('display_name', 'first_name', 'last_name', 'short_intro', 'bio', 
                  'link_twitter', 'link_linkedin', 'link_youtube', 'link_facebook', 'link_website')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('email', 'password', 'profile')

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            register_method="email",
        )

        Profile.objects.update_or_create(user=user, defaults=profile_data)
        return user

