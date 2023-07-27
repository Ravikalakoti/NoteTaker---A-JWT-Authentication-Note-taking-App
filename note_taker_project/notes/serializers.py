# notes/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from notes.models import Note, NoteSharingInvitation

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class TokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = User.objects.filter(username=email).first()

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
        else:
            raise serializers.ValidationError("Invalid credentials.")

        return data


class NoteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'user')


class NoteSharingInvitationSerializer(serializers.Serializer):
    users = serializers.ListField(child=serializers.CharField( max_length=100), write_only=True, required=False)