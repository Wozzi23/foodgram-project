from rest_framework import serializers

from recipes.models import Ingredients
from users.models import User


class SignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели User.
    """

    class Meta:
        model = User
        read_only_fields = ('id',)
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class IngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Ingredients.
    """

    class Meta:
        model = Ingredients
        read_only_fields = ('id', 'name', 'measurement_unit')
        fields = ('id', 'name', 'measurement_unit')