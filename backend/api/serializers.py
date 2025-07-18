from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Post, Trees, comments, Community

class UserSerializer(serializers.ModelSerializer):
    Profile_picture = serializers.ImageField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'Profile_picture']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_picture = validated_data.pop('Profile_picture', None)
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        if profile_picture:
            user.profile.profile_picture = profile_picture
            user.profile.save()
        return user

class TreeSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Trees
        fields = '__all__'
        read_only_fields = ['user']

    def get_username(self, obj):
        return obj.user.username

class PostSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    userId = serializers.SerializerMethodField()
    loginUserProfile = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'post_text', 'username', 'picture', 'loginUserProfile', 'like_count', 'profile_picture', 'likes', 'userId', 'latitude', 'longitude']
        read_only_fields = ['username', 'author', 'like_count', 'loginUserProfile', 'profile_picture', 'userId']

    def get_username(self, obj):
        return obj.author.username

    def get_like_count(self, obj):
        return obj.like_count

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.author.profile and obj.author.profile.profile_picture:
            return request.build_absolute_uri(obj.author.profile.profile_picture.url)
        return None

    def get_loginUserProfile(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                profile = request.user.profile
                return request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None
            except Profile.DoesNotExist:
                return None
        return None

    def get_userId(self, obj):
        request = self.context.get('request')
        return request.user.id if request and request.user.is_authenticated else None

class userPostSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    userId = serializers.SerializerMethodField()
    loginUserProfile = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'post_text', 'username', 'picture', 'loginUserProfile', 'like_count', 'likes', 'userId', 'latitude', 'longitude']
        read_only_fields = ['username', 'author', 'like_count', 'loginUserProfile', 'userId']

    def get_username(self, obj):
        return obj.author.username

    def get_like_count(self, obj):
        return obj.like_count

    def get_loginUserProfile(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                return request.build_absolute_uri(request.user.profile.profile_picture.url)
            except Profile.DoesNotExist:
                return None
        return None

    def get_userId(self, obj):
        request = self.context.get('request')
        return request.user.id if request and request.user.is_authenticated else None

class commentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = comments
        fields = '__all__'
        read_only_fields = ['user']

class postcommentsSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    picture = serializers.SerializerMethodField()

    class Meta:
        model = comments
        fields = ['id', 'text', 'date', 'user', 'post', 'username', 'picture']
        read_only_fields = ['user']

    def get_username(self, obj):
        return obj.user.username

    def get_picture(self, obj):
        return obj.user.profile.profile_picture.url

class CommunitySerializer(serializers.ModelSerializer):
    trees = TreeSerializer(many=True, read_only=True)
    members = UserSerializer(many=True, read_only=True)
    is_member = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = '__all__'
        read_only_fields = ['created_by', 'is_member']

    def get_is_member(self, obj):
        request = self.context.get('request')
        if request:
            return obj.members.filter(id=request.user.id).exists()
        return False

from dj_rest_auth.registration.serializers import RegisterSerializer

class CustomRegistrationSerializer(RegisterSerializer):
    profile_picture = serializers.ImageField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)

    def save(self, request):
        user = super().save(request)
        profile_picture = self.validated_data.get('profile_picture', None)
        first_name = self.validated_data.get('first_name', None)
        last_name = self.validated_data.get('last_name', None)

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.save()

        profile, created = Profile.objects.get_or_create(user=user)
        if profile_picture:
            profile.profile_picture = profile_picture
            profile.save()

        return user