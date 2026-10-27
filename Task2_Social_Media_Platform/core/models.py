from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import re
import urllib.parse


class Profile(models.Model):
    THEME_CHOICES = [
        ('dark', 'Dark Theme'),
        ('light', 'Light Theme'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=60, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=300, blank=True)
    pronouns = models.CharField(max_length=30, blank=True, default='')
    campus = models.CharField(max_length=100, blank=True, default='', help_text="e.g. NYU '26, UCLA Design")
    interests = models.CharField(max_length=250, blank=True, default='', help_text="Comma-separated interests")
    vibe_tag = models.CharField(max_length=50, blank=True, default='Vibe Architect')
    website = models.URLField(max_length=200, blank=True, default='')
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='dark')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"@{self.user.username} ({self.get_display_name()})"

    def get_display_name(self):
        return self.display_name.strip() if self.display_name else self.user.username

    def get_avatar_url(self):
        if self.avatar:
            try:
                return self.avatar.url
            except Exception:
                pass
        # Gen-Z friendly dynamic avatar generator based on username
        encoded = urllib.parse.quote(self.user.username)
        return f"https://api.dicebear.com/7.x/bottts-neutral/svg?seed={encoded}&backgroundColor=b6e3f4,c0aede,d1d4f9,ffd5dc,ffdfbf"

    def get_interests_list(self):
        if not self.interests:
            return []
        return [item.strip() for item in self.interests.split(',') if item.strip()]

    @property
    def posts_count(self):
        return self.user.posts.count()

    @property
    def followers_count(self):
        return self.user.follower_set.count()

    @property
    def following_count(self):
        return self.user.following_set.count()

    def is_followed_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.user.follower_set.filter(follower=user).exists()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()


class Post(models.Model):
    MOOD_CHOICES = [
        ('', '✨ No Mood Tag'),
        ('🎧 In My Zone', '🎧 In My Zone'),
        ('☕ Campus Grind', '☕ Campus Grind'),
        ('💀 Brain Rot', '💀 Brain Rot'),
        ('✨ Feeling Iconic', '✨ Feeling Iconic'),
        ('🌙 Midnight Musings', '🌙 Midnight Musings'),
        ('⚡ Unhinged Energy', '⚡ Unhinged Energy'),
        ('🍕 Late Night Craving', '🍕 Late Night Craving'),
        ('🎨 Creative Surge', '🎨 Creative Surge'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=1000)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    mood = models.CharField(max_length=50, choices=MOOD_CHOICES, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by @{self.author.username} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()

    def extract_hashtags(self):
        tags = re.findall(r'#(\w+)', self.content)
        return list(dict.fromkeys(tags))  # unique preserving order


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by @{self.author.username} on #{self.post.id}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['user', 'post']),
        ]

    def __str__(self):
        return f"@{self.user.username} liked Post #{self.post.id}"


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower', 'following']),
        ]

    def __str__(self):
        return f"@{self.follower.username} follows @{self.following.username}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('like', 'Liked your post'),
        ('comment', 'Commented on your post'),
        ('follow', 'Started following you'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='post_notifications')
    text = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for @{self.recipient.username}: {self.actor.username} {self.get_notification_type_display()}"
