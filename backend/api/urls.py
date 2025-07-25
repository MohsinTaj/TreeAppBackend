
from django.urls import path,include, re_path
from .views import *


from django.contrib.auth.views import LoginView

from dj_rest_auth.registration.views import VerifyEmailView

from django.views.generic import TemplateView

urlpatterns = [
    # path('picture/',PictureGetCreate.as_view(),name='picture'),
    path('signup/',signup),
    # path('login/', LoginView.as_view(), name='login'),
    path('test_token',test_token),
    path('dj-rest-auth/',include('dj_rest_auth.urls')),
    path('trees/',TreeListCreateView.as_view(), name ='tree-list-create'),
    path('trees/<int:pk>/',TreeDetailView.as_view(), name ='tree-detail'),
    path('user_profile/',get_user_profile, name ='user-profile'),
    path('user_trees/',get_user_trees, name ='user-trees'),
    path('api/trees/all/', all_trees_with_details, name='all-trees'),
    path('community_trees/<int:comm_id>/',get_Community_trees, name ='community-trees'),
    path('community_joined/',get_user_communities, name ='user-community'),
    path('user_trees_count/',get_user_trees_count, name ='user-trees_count'),
    path('leaderboard/',get_leaderboard, name ='user-trees'),    
    path('user_trees_count/',get_user_trees_count, name ='user-trees'),
    path('posts/',PostListCreateView.as_view(), name ='post-list-create'),
    path('posts/<int:pk>/',PostDetailView.as_view(), name ='post-detail'),
    path('comments/',commentsListCreateView.as_view(), name ='comments-list-create'),
    path('comments/<int:pk>/',commentsDetailView.as_view(), name ='comments-detail'),
    path('post_comments/<int:id>/',get_comments, name ='post-comments'),
    path('google-user/', google_user, name='google-sign-in'),
    path('top-members/<int:community_id>/', top_community_members, name='top-community-members'),
    path('user_posts/',get_user_posts, name ='post-comments'),


    # mehak
    path('communities/', CommunityListCreateView.as_view(), name='community-list-create'),
    path('communities/<int:pk>/join/', JoinCommunityView.as_view(), name='join-community'),
    path('communities/<int:pk>/leave/', LeaveCommunityView.as_view(), name='leave-community'),
    path('communities/<int:pk>/', CommunityDetailView.as_view(), name='community-detail'),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    # path('custom-registration/', CustomRegisterView.as_view(), name='custom-registration'),
    path('dj-rest-auth/account-confirm-email/<str:key>/', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    path('email-verification-success/', TemplateView.as_view(template_name='account/email_verification_success.html'), name='email-verification-success'),
    path('email-verification-failed/', TemplateView.as_view(template_name='account/email_verification_failed.html'), name='email-verification-failed'),
    re_path('verify-email/(?P<key>[-:\w]+)/$', CustomEmailVerifyView.as_view(), name='account_email_verification'),


    # path('auth/', include('djoser.urls')),

]