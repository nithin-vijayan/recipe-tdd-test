from rest_framework import serializers
from core.models import Tag, Intgredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag object"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ['id']


class IntgredientSerializer(serializers.ModelSerializer):
    """Serializer for Intgredient object"""

    class Meta:
        model = Intgredient
        fields = ('id', 'name')
        read_only_fields = ['id']
