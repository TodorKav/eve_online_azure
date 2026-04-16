from django.contrib.auth import get_user_model
from rest_framework import serializers

UserModel = get_user_model()

class UserCreateApiSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = UserModel
        fields = ('username', 'email', 'password')


    def create(self, validated_data):
        username = validated_data.get('username', None)
        email = validated_data.get('email', None)
        password = validated_data.get('password', None)
        user = UserModel.objects.create_user(username=username, email=email, password=password)
        return user