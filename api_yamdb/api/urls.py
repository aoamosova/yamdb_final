from api.views import (AdminUserViewSet, CategoryViewSet, CommentViewSet,
                       GenreViewSet, GetTokenViewSet, ReviewViewSet,
                       TitleViewSet, UserViewSet)
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()
router.register('users', AdminUserViewSet, basename='admin_user')
router.register('titles', TitleViewSet)
router.register('genres', GenreViewSet)
router.register('categories', CategoryViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

auth_router = routers.DefaultRouter()
auth_router.register('signup', UserViewSet, basename='signup')
auth_router.register('token', GetTokenViewSet, basename='token')


urlpatterns = [
    path('v1/auth/', include(auth_router.urls)),
    path('v1/', include(router.urls))
]
