from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='products_images/', null=True, blank=True)

# Signal to create or update profile automatically
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

class Community(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='communities_created')
    members = models.ManyToManyField(User, related_name='communities_joined')
    created_at = models.DateTimeField(auto_now_add=True)
    community_picture = models.ImageField(upload_to='community_images/', null=True, blank=True)

    def add_member(self, user):
        if not self.members.filter(id=user.id).exists():
            self.members.add(user)
            self.save()
            return True
        return False

    def remove_member(self, user):
        if self.members.filter(id=user.id).exists():
            self.members.remove(user)
            self.save()
            return True
        return False

    def __str__(self):
        return self.name

class Trees(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trees')
    name = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='products_images/', null=True, blank=True)
    latitude = models.FloatField(blank=True, null=True)  # Changed max_length to blank=True, null=True
    longitude = models.FloatField(blank=True, null=True)  # Changed max_length to blank=True, null=True
    creat_date = models.DateTimeField(default=timezone.now)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, blank=True, related_name='trees')

    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    post_text = models.CharField(max_length=1000)
    picture = models.ImageField(upload_to='products_images/', null=True, blank=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    latitude = models.FloatField(blank=True, null=True)  # Added field
    longitude = models.FloatField(blank=True, null=True)  # Added field

    @property
    def like_count(self):
        return self.likes.count()

class comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)