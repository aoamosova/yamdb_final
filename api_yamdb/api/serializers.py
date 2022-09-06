from django.conf import settings
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from reviews.models import Categories, Comments, Genres, Review, Title, User


class FullUserSerializer(serializers.ModelSerializer):
    """Serializer for user model with all fields"""
    class Meta:
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'role', 'email')
        model = User


class UserEmailCodeSerializer(serializers.Serializer):
    """Serializer for checking code from user."""
    username = serializers.CharField(required=True, max_length=128)
    confirmation_code = serializers.IntegerField(required=True)

    def validate(self, data):
        confirmation_code = data['confirmation_code']
        user = get_object_or_404(User, username=data['username'])
        if confirmation_code == settings.RESET_CONFIRMATION_CODE:
            raise serializers.ValidationError(
                ('Данный код подтверждения уже использовался.'
                 'Получите новый через регистрацию'))
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError('Неверный код подтверждения')
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registrations with email and username."""

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError('Username "me" уже занято.')
        return data


class TitleSerialiser(serializers.ModelSerializer):
    """Serializer for title model with all fields"""
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genres.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Categories.objects.all()
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Title

    def get_rating(self, obj):
        return get_reting_titles(obj)


class GenreSerialiser(serializers.ModelSerializer):
    """Serializer for genre model with exclude"""
    class Meta:
        model = Genres
        exclude = ('id',)
        lookup_fields = 'slug'
        extra_kwargs = {
            'url': {'lookup_fields': 'slug'}
        }


class CategorySerialiser(serializers.ModelSerializer):
    """Serializer for genre model with exclude"""
    class Meta:
        model = Categories
        exclude = ('id',)
        lookup_fields = 'slug'
        extra_kwargs = {
            'url': {'lookup_fields': 'slug'}
        }


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    """Serializer for read only title model with all fields"""
    genre = GenreSerialiser(many=True)
    category = CategorySerialiser()
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'name', 'year', 'description',
                  'category', 'genre', 'rating')
        model = Title

    def get_rating(self, obj):
        return get_reting_titles(obj)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    title = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Title.objects.all(),
        read_only=False,
        required=False
    )

    class Meta:
        fields = '__all__'
        model = Review

    def create(self, validated_data):
        count_review_title = Review.objects.filter(
            author=validated_data.get('author'),
            title=validated_data.get('title')
        ).count()
        if count_review_title == 1:
            raise serializers.ValidationError('Нет')
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    title = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Title.objects.all(),
        read_only=False,
        required=False
    )
    review = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Review.objects.all(),
        read_only=False,
        required=False
    )

    class Meta:
        fields = '__all__'
        model = Comments
        read_only_fields = ('author',)


def get_reting_titles(title):
    """calculation of the rating of the title"""
    avg_score = title.reviews.aggregate(average_price=Avg("score"))
    if not avg_score['average_price']:
        return None
    return int(avg_score['average_price'])
