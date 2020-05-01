from rest_framework import serializers
from core.models import Tag, Intgredient, Recipe


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


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model"""
    intgredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Intgredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'title', 'intgredients', 'tags', 'time_minutes', 'price',
            'link',
            )
        read_only_fields = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    """Serialize recipe details"""
    intgredients = IntgredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
