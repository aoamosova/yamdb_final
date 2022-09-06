from api.filters import TitleFilter
from api.mixins import ListCreateDestroyViewSet
from api.permissions import (IsAdminOrReadOnly, IsAdminOrSuperUser,
                             IsAuthorOrReadOnly)
from api.serializers import (CategorySerialiser, CommentSerializer,
                             FullUserSerializer, GenreSerialiser,
                             ReadOnlyTitleSerializer, ReviewSerializer,
                             TitleSerialiser, UserEmailCodeSerializer,
                             UserSerializer)
from api.utils import email_code, send_email
from django.conf import settings
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters, mixins, pagination, permissions, status,
                            viewsets)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Categories, Genres, Title, User


class AdminUserViewSet(viewsets.ModelViewSet):
    """API for admin actions: get, post, patch, delete users info.
    """
    queryset = User.objects.all()
    serializer_class = FullUserSerializer
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    permission_classes = (IsAdminOrSuperUser,)
    pagination_class = pagination.LimitOffsetPagination
    search_fields = ('username',)

    @action(detail=False, url_path='me', methods=['GET', 'PATCH'],
            permission_classes=(permissions.IsAuthenticated,))
    def user_get_patch_page(self, request):
        """
        Add "me" page for authenticated user: /users/me

        Returns:
            Response object

        """
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(role=user.role, partial=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """API for user registration with username and email on page auth/signup/.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )

    def perform_create(self, serializer):
        code = email_code()
        send_email(serializer.validated_data.get('email'), code)
        serializer.save(confirmation_code=code)


class GetTokenViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """API for generating token response.
    """
    queryset = User.objects.all()
    serializer_class = UserEmailCodeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)
        user = get_object_or_404(
            User, username=serializer.data.get('username')
        )
        user.confirmation_code = settings.RESET_CONFIRMATION_CODE
        user.save()
        token = AccessToken.for_user(user)
        return Response(
            {'token': str(token)}, status=status.HTTP_200_OK, headers=headers)


class TitleViewSet(viewsets.ModelViewSet):
    """ This viewset automatically provides `list`, `create`, `retrieve`,
        `update`, `partial_update` and `destroy` actions.
    """
    queryset = Title.objects.all()
    serializer_class = TitleSerialiser
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadOnlyTitleSerializer
        return TitleSerialiser


class GenreViewSet(ListCreateDestroyViewSet):
    """ This viewset automatically provides `list`, `create`, `destroy` actions.
    """
    queryset = Genres.objects.all()
    serializer_class = GenreSerialiser
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(ListCreateDestroyViewSet):
    """ This viewset automatically provides `list`, `create`, `destroy` actions.
    """
    queryset = Categories.objects.all()
    serializer_class = CategorySerialiser
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update`, `partial_update` and `destroy` actions.
    """
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        title = get_title(self.kwargs['title_id'])
        queryset = title.reviews.all()
        return queryset

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=get_title(self.kwargs['title_id'])
        )


class CommentViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update`, `partial_update` and `destroy` actions.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        title = get_title(self.kwargs['title_id'])
        review = get_review(title, self.kwargs['review_id'])
        queryset = review.comments.all()
        return queryset

    def perform_create(self, serializer):
        title = get_title(self.kwargs['title_id'])
        review = get_review(title, self.kwargs['review_id'])
        serializer.save(
            author=self.request.user,
            title=title,
            review=review
        )


def get_title(title_id):
    """the function gets the object by id"""
    return get_object_or_404(Title, id=title_id)


def get_review(title, review_id):
    """the function gets the object by id"""
    return title.reviews.get(id=review_id)
