from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.db.models import Count
from .serializers import *
import requests
from django.core.files.base import ContentFile
from allauth.account.models import EmailConfirmationHMAC
from allauth.account.utils import send_email_confirmation
from django.views import View
import logging
from django.http import HttpResponse

logger = logging.getLogger(__name__)

# Create your views here.
# class PictureGetCreate(generics.ListCreateAPIView): #show and create data
#     queryset =Picture.objects.all()
#     serializer_class = PictureSerializer

# class PictureUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
#     queryset =Picture.objects.all()
#     serializer_class = PictureSerializer

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
@csrf_exempt
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
       return Response({"detail":"Not found"},status=status.HTTP_400_BAD_REQUEST)
    token,created =Token.objects.get_or_create(user=user)
    serializer =UserSerializer(instance=user)
    return Response({ "token":token.key,"user":serializer.data},content_type='application/json')

# @csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
@csrf_exempt
def signup(request):
    #initialise a serialiser based on the request data came in for signup call
    serializer = UserSerializer(data=request.data) #files=request.FILES
    if serializer.is_valid():
        user = serializer.save()  # UserSerializer's create method handles profile picture
        token = Token.objects.create(user=user)
        user_data = serializer.data
        user_data['profile_picture'] = user.profile.profile_picture.url if user.profile.profile_picture else None
        user_data['first_name'] = user.first_name
        user_data['last_name'] = user.last_name
        return Response({"token": token.key, "user": user_data}, content_type='application/json')
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST, content_type='application/json')

@authentication_classes([SessionAuthentication,TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def test_token(request):
    #method to test our off token to make sure they work for bad req
    return Response("passed for {}".format(request.user.email))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    try:
        user = request.user
        profile = get_object_or_404(Profile, user=user)
        user_data = UserSerializer(user).data
        user_data['profile_picture'] = profile.profile_picture.url if profile.profile_picture else None
        return Response(user_data, status=status.HTTP_200_OK)
    except Profile.DoesNotExist:
        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

class TreeListCreateView(generics.ListCreateAPIView):
    queryset = Trees.objects.all()
    serializer_class = TreeSerializer
    authentication_classes = [TokenAuthentication]  # Use token authentication
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Assign the authenticated user from the request to the user field
        serializer.save(user=self.request.user)

class TreeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset =Trees.objects.all()
    serializer_class = TreeSerializer

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-id')
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        # Assign the authenticated user from the request to the user field
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset =Post.objects.all()
    serializer_class = PostSerializer

class commentsListCreateView(generics.ListCreateAPIView):
    queryset = comments.objects.all()
    serializer_class = commentsSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class commentsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset =comments.objects.all()
    serializer_class = commentsSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_trees(request):
    try:
        user =request.user
        trees = Trees.objects.filter(user=user)
        serializer =TreeSerializer(trees, many =True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "Tree not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_communities(request):
    try:
        user= request.user
        communities = user.communities_joined.all()
        serializer =CommunitySerializer(communities,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    except Community.DoesNotExist:
        return Response({"error":"Tree not found"},status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_comments(request,id):
    try:
        comment=comments.objects.filter(post_id=id)
        serializer =postcommentsSerializer(comment, many =True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except comments.DoesNotExist:
        return Response({"error": "comments not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_user_posts(request):
    try:
        user = request.user if request.user.is_authenticated else None
        posts = Post.objects.filter(author_id=user.id).order_by('-id') if user else Post.objects.all().order_by('-id')
        serializers = userPostSerializer(posts, many=True, context={'request': request})
        return Response(serializers.data, status=status.HTTP_200_OK)
    except Post.DoesNotExist:
        return Response({"error": "Posts not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_Community_trees(request, comm_id):
    try:
        trees = Trees.objects.filter(community_id=comm_id)
        serializer =TreeSerializer(trees, many =True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Trees.DoesNotExist:
        return Response({"error": "Tree not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_trees_count(request):
    try:
        user =request.user
        trees = Trees.objects.filter(user=user).count()
        # serializer =TreeSerializer(trees, many =True)
        return Response({'tree count':trees}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

from django.db.models import Count

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_leaderboard(request):
    try:
        users_with_trees = User.objects.annotate(tree_count=Count('trees')).order_by('-tree_count')
        userdata = []

        position=0
        currentposition=None
        for user in users_with_trees:
            position=position+1
            profile_picture = None
            if(request.user.id==user.id):
                currentposition =position
            if hasattr(user, 'profile'):
                profile_picture = user.profile.profile_picture.url if user.profile.profile_picture else None

            userdata.append({
                'first_name': user.first_name,
                'last_name': user.last_name,
                'usertree': user.tree_count,
                'profile_picture': profile_picture,
                'position':position,
                'currentposition':currentposition if position==currentposition else None
            })
        return Response(userdata,status=200)
    except Exception as e:
        return Response({'error':str(e)},status=500)

# mehak
class CommunityListCreateView(generics.ListCreateAPIView):
    '''
        IF GET -> List
        IF POST -> Create
    '''
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        community = serializer.save(created_by=self.request.user)
        community.members.add(self.request.user)
        community.save()

    def get_serializer_context(self):
        return {'request': self.request}

class JoinCommunityView(generics.UpdateAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        community = self.get_object()
        if community.add_member(request.user):
            return Response({"detail": "You have successfully joined the community"})
        return Response({"detail": "You are already a member of this community"}, status = status.HTTP_400_BAD_REQUEST)

class LeaveCommunityView(generics.UpdateAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        community = self.get_object()
        if request.user == community.created_by:
            return Response({"detail": "You cannot leave a community you created"}, status = status.HTTP_400_BAD_REQUEST)
        if community.remove_member(request.user):
            return Response({"detail": "You have successfully left the community"})
        return Response({"detail": "You are not a member of this community"}, status = status.HTTP_400_BAD_REQUEST)

class CommunityDetailView(generics.RetrieveAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticated]

# from .serializers import CustomRegistrationSerializer

# class CustomRegisterView(generics.CreateAPIView):
#     serializer_class = CustomRegistrationSerializer
#
#     def post(self, request, *args, **kwargs):
#         print("Hello from inside the custom view")  # Debugging statement
#         return super().post(request, *args, **kwargs)
#
#     def perform_create(self, serializer):
#         serializer.save(request=self.request)

class TopCommunityView(generics.ListAPIView):
    queryset = Community.objects.annotate(tree_count=Count('trees')).order_by('-tree_count')[:3]
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticated]

def check_google_login(request):
    print("Google login called")
    print("Request data: ", request.data)
    return Response({"detail": "Google login called"})

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def top_community_members(request, community_id):
    try:
        community = Community.objects.get(id=community_id)
        members = User.objects.filter(communities_joined=community).annotate(tree_count=Count('trees')).order_by('-tree_count')[:3]
        serializer = UserSerializer(members, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({"error": "No members to return"}, status=status.HTTP_404_NOT_FOUND)

import requests
from django.core.files.base import ContentFile

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def google_user(request):
    data = request.data
    uid = data.get('uid')
    email = data.get('email')
    display_name = data.get('displayName')
    photo_url = data.get('photoURL')

    if not uid or not email:
        return Response({'status': 'error', 'message': 'UID and email are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Extract the username from the email
    username = email.split('@')[0]

    try:
        # Get or create the user with the specified username
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )

        if created:
            # If the user was created, set an unusable password
            user.set_unusable_password()
            user.save()

        # Handle profile picture if provided
        if photo_url:
            response = requests.get(photo_url)
            if response.status_code == 200:
                # Save the image to the user's profile
                user.profile.profile_picture.save(
                    f'{user.username}_profile.jpg',
                    ContentFile(response.content),
                    save=True
                )

        # Generate or get the token for the user
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'status': 'success', 'token': token.key, 'username': user.username}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from allauth.account.models import EmailConfirmationHMAC
from allauth.account.utils import send_email_confirmation
from django.views import View

import logging
from django.http import HttpResponse

logger = logging.getLogger(__name__)

class CustomEmailVerifyView(View):
    def get(self, request, key):
        if not key:
            return HttpResponse("<h5>Invalid verification key.</h5>", status=400)

        try:
            email_confirmation = EmailConfirmationHMAC.from_key(key)
            if email_confirmation:
                email_confirmation.confirm(request)
                return HttpResponse("<h5>Email verified successfully. You can return to the app.</h5>", status=200)
            else:
                return HttpResponse("<h5>Invalid or expired verification key.</h5>", status=400)
        except Exception as e:
            logger.error(f"Error during email confirmation: {e}")
            return HttpResponse("<h5>An error occurred during email verification. Please try again later.</h5>", status=500)