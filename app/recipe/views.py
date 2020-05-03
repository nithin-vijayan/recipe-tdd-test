from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Tag, Ingredient, Recipe
from recipe import serializers


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base recipe attribute class"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for current user"""
        queryset = self.queryset
        assigned_true = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        if assigned_true:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user).order_by(
                '-name'
                ).distinct()

    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage Ingredients in db"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in db"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_int(self, param_string):
        """Convert query parameters to int id list"""
        return [int(id_) for id_ in param_string.split(',')]

    def get_queryset(self):
        """Retrieve recies for authenticated user"""
        params_tag = self.request.query_params.get('tags')
        params_ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if params_tag:
            ids = self._params_to_int(params_tag)
            queryset = queryset.filter(tags__id__in=ids)
        if params_ingredients:
            ids = self._params_to_int(params_ingredients)
            queryset = queryset.filter(ingredients__id__in=ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create new recipe"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload image to db"""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST
            )
