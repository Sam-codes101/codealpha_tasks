from django.contrib import admin
from .models import Profile, Post, Comment, Like, Follow, Notification


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'campus', 'vibe_tag', 'theme_preference', 'created_at')
    search_fields = ('user__username', 'display_name', 'campus', 'interests')
    list_filter = ('theme_preference', 'campus')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'mood', 'likes_count', 'comments_count', 'created_at')
    search_fields = ('author__username', 'content', 'mood')
    list_filter = ('mood', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'content_snippet', 'created_at')
    search_fields = ('author__username', 'content')
    list_filter = ('created_at',)

    def content_snippet(self, obj):
        return obj.content[:40] + '...' if len(obj.content) > 40 else obj.content


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    search_fields = ('user__username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'actor', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'actor__username', 'text')
