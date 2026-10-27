from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
import json
import re

from .models import Profile, Post, Comment, Like, Follow, Notification
from .forms import SignUpForm, CustomLoginForm, PostForm, CommentForm, ProfileUpdateForm, UserUpdateForm


# -------------------------------------------------------------
# HELPER UTILITIES
# -------------------------------------------------------------

def get_trending_hashtags(limit=6):
    """Dynamically aggregate hashtags across recent posts."""
    posts = Post.objects.all().order_by('-created_at')[:100]
    hashtag_counts = {}
    for post in posts:
        tags = post.extract_hashtags()
        for tag in tags:
            tag_clean = tag.lower()
            hashtag_counts[tag_clean] = hashtag_counts.get(tag_clean, 0) + 1

    sorted_tags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    return [{'tag': item[0], 'count': item[1]} for item in sorted_tags]


def get_suggested_users(current_user, limit=4):
    """Suggest active users the current user does not follow yet."""
    if not current_user.is_authenticated:
        return User.objects.all().exclude(is_superuser=True).order_by('-date_joined')[:limit]

    following_ids = Follow.objects.filter(follower=current_user).values_list('following_id', flat=True)
    suggested = User.objects.exclude(id=current_user.id)\
                            .exclude(id__in=following_ids)\
                            .exclude(is_superuser=True)

    # Match by campus or shared interests if possible
    if hasattr(current_user, 'profile'):
        my_interests = [i.strip().lower() for i in current_user.profile.get_interests_list()]
        my_campus = (current_user.profile.campus or '').strip().lower()

        if my_interests or my_campus:
            # Score or filter users
            interest_query = Q()
            if my_campus:
                interest_query |= Q(profile__campus__icontains=my_campus)
            for interest in my_interests:
                interest_query |= Q(profile__interests__icontains=interest)

            relevant = suggested.filter(interest_query).distinct()[:limit]
            if relevant.count() >= 2:
                return relevant

    return suggested.order_by('-date_joined')[:limit]


def create_notification(recipient, actor, notification_type, post=None, text=''):
    """Helper to create notifications safely without self-notification or duplicate noise."""
    if recipient == actor:
        return None

    # Check for existing unread like notification to prevent spamming
    if notification_type == 'like' and post:
        existing = Notification.objects.filter(
            recipient=recipient,
            actor=actor,
            notification_type='like',
            post=post,
            is_read=False
        ).first()
        if existing:
            return existing

    notif = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notification_type=notification_type,
        post=post,
        text=text
    )
    return notif


# -------------------------------------------------------------
# AUTH & LANDING
# -------------------------------------------------------------

def landing_view(request):
    """High energy Gen-Z landing page for guests; redirects logged-in users to home feed."""
    if request.user.is_authenticated:
        return redirect('home')

    sample_posts = Post.objects.select_related('author', 'author__profile').order_by('-created_at')[:3]
    recent_users = User.objects.exclude(is_superuser=True).order_by('-date_joined')[:6]
    total_posts = Post.objects.count()
    total_users = User.objects.count()

    context = {
        'sample_posts': sample_posts,
        'recent_users': recent_users,
        'total_posts': total_posts,
        'total_users': total_users,
        'trending_tags': get_trending_hashtags(4),
    }
    return render(request, 'landing.html', context)


def signup_view(request):
    """User registration with Gen-Z validation feedback."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Ensure profile exists with initial vibe tag
            profile = user.profile
            profile.display_name = user.username.capitalize()
            profile.save()

            # Log the new user in
            login(request, user)
            messages.success(request, f"Welcome to the chaos, @{user.username}! ✨ Your vibe is officially verified.")
            return redirect('home')
        else:
            messages.error(request, "Oops! Check the errors below to join the vibe.")
    else:
        form = SignUpForm()

    return render(request, 'auth/signup.html', {'form': form})


def login_view(request):
    """User authentication with clean feedback."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, @{user.username}! Good to see you.")
            next_url = request.GET.get('next') or 'home'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Double-check your credentials!")
    else:
        form = CustomLoginForm()

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """Log out user with friendly sign-off."""
    logout(request)
    messages.info(request, "Catch you later! Stay iconic. ✨")
    return redirect('landing')


# -------------------------------------------------------------
# HOME FEED & POSTS
# -------------------------------------------------------------

@login_required
def home_feed_view(request):
    """Home feed showing posts from followed users with a fallback tab for 'All / For You'."""
    tab = request.GET.get('feed', 'following')  # 'following' or 'all'
    user = request.user

    following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)

    if tab == 'following':
        # Posts from followed users and the user themselves
        feed_user_ids = list(following_ids) + [user.id]
        post_queryset = Post.objects.filter(author_id__in=feed_user_ids)\
                                    .select_related('author', 'author__profile')\
                                    .prefetch_related('likes', 'comments')
        # If user isn't following anyone yet, show helpful empty state or prompt
    else:
        # 'For You' / Global feed
        post_queryset = Post.objects.all()\
                                    .select_related('author', 'author__profile')\
                                    .prefetch_related('likes', 'comments')

    paginator = Paginator(post_queryset, 10)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)

    # Attach liked_by_current_user to avoid N+1 queries in template
    user_liked_post_ids = set(Like.objects.filter(user=user, post__in=posts).values_list('post_id', flat=True))
    for post in posts:
        post.has_liked = post.id in user_liked_post_ids

    form = PostForm()
    trending_tags = get_trending_hashtags()
    suggested_users = get_suggested_users(user)

    context = {
        'posts': posts,
        'form': form,
        'tab': tab,
        'following_count': len(following_ids),
        'trending_tags': trending_tags,
        'suggested_users': suggested_users,
    }
    return render(request, 'feed/home.html', context)


@login_required
def create_post_view(request):
    """Create a new post via standard form or AJAX."""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Post is live ✨',
                    'post_id': post.id
                })

            messages.success(request, "Post is live ✨")
            return redirect('home')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = [str(err) for err in form.errors.values()]
                return JsonResponse({'status': 'error', 'errors': errors}, status=400)
            messages.error(request, "Could not publish post. Please check the content.")
            return redirect('home')

    return render(request, 'feed/create_post.html', {'form': PostForm()})


@login_required
def edit_post_view(request, pk):
    """Edit existing post (author only)."""
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("You cannot edit someone else's post!")

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully! 🪄")
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'feed/edit_post.html', {'form': form, 'post': post})


@login_required
@require_POST
def delete_post_view(request, pk):
    """Delete post (author only)."""
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("You cannot delete someone else's post!")

    post.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Post deleted.'})

    messages.info(request, "Post vanished into the digital void 💨")
    return redirect('home')


def post_detail_view(request, pk):
    """View a single post with comments."""
    post = get_object_or_404(
        Post.objects.select_related('author', 'author__profile'),
        pk=pk
    )
    comments = post.comments.select_related('author', 'author__profile').all()
    comment_form = CommentForm()

    has_liked = False
    if request.user.is_authenticated:
        has_liked = post.is_liked_by(request.user)

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'has_liked': has_liked,
    }
    return render(request, 'feed/post_detail.html', context)


# -------------------------------------------------------------
# COMMENTS & LIKES (AJAX + Form Fallbacks)
# -------------------------------------------------------------

@login_required
@require_POST
def like_toggle_view(request, pk):
    """Toggle like on a post, returns JSON response."""
    post = get_object_or_404(Post, pk=pk)
    user = request.user

    like_obj = Like.objects.filter(user=user, post=post).first()
    if like_obj:
        like_obj.delete()
        liked = False
    else:
        Like.objects.create(user=user, post=post)
        liked = True
        create_notification(
            recipient=post.author,
            actor=user,
            notification_type='like',
            post=post
        )

    likes_count = post.likes.count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'status': 'success',
            'liked': liked,
            'likes_count': likes_count
        })

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
@require_POST
def add_comment_view(request, pk):
    """Add comment to a post."""
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

        # Send notification to post author
        create_notification(
            recipient=post.author,
            actor=request.user,
            notification_type='comment',
            post=post,
            text=comment.content[:80]
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'comment_id': comment.id,
                'author_username': comment.author.username,
                'author_name': comment.author.profile.get_display_name(),
                'author_avatar': comment.author.profile.get_avatar_url(),
                'content': comment.content,
                'created_at': 'Just now',
                'comments_count': post.comments.count()
            })

        messages.success(request, "Thought dropped! 💬")
        return redirect('post_detail', pk=post.pk)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    messages.error(request, "Comment could not be published.")
    return redirect('post_detail', pk=post.pk)


@login_required
@require_POST
def delete_comment_view(request, pk):
    """Delete a comment (author only)."""
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post

    if comment.author != request.user and post.author != request.user:
        return HttpResponseForbidden("You are not authorized to delete this comment.")

    comment.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Comment removed',
            'comments_count': post.comments.count()
        })

    messages.info(request, "Comment deleted.")
    return redirect('post_detail', pk=post.pk)


# -------------------------------------------------------------
# EXPLORE & SEARCH
# -------------------------------------------------------------

def explore_view(request):
    """Explore page with search for posts & users, trending hashtags, and suggested accounts."""
    query = request.GET.get('q', '').strip()
    tag = request.GET.get('tag', '').strip()
    mood_filter = request.GET.get('mood', '').strip()

    posts = Post.objects.select_related('author', 'author__profile').prefetch_related('likes', 'comments')
    matching_users = []

    if query:
        # Search both posts content and user profiles
        posts = posts.filter(
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(author__profile__display_name__icontains=query)
        )
        matching_users = User.objects.filter(
            Q(username__icontains=query) |
            Q(profile__display_name__icontains=query) |
            Q(profile__bio__icontains=query) |
            Q(profile__campus__icontains=query) |
            Q(profile__interests__icontains=query)
        ).exclude(is_superuser=True).distinct()[:10]

    elif tag:
        # Hashtag filter
        posts = posts.filter(content__icontains=f"#{tag}")

    elif mood_filter:
        posts = posts.filter(mood=mood_filter)

    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page', 1)
    posts_page = paginator.get_page(page_number)

    if request.user.is_authenticated:
        user_liked_post_ids = set(Like.objects.filter(user=request.user, post__in=posts_page).values_list('post_id', flat=True))
        for post in posts_page:
            post.has_liked = post.id in user_liked_post_ids

    trending_tags = get_trending_hashtags(8)
    suggested_users = get_suggested_users(request.user, limit=5)

    context = {
        'posts': posts_page,
        'query': query,
        'tag': tag,
        'mood_filter': mood_filter,
        'matching_users': matching_users,
        'trending_tags': trending_tags,
        'suggested_users': suggested_users,
        'mood_choices': Post.MOOD_CHOICES,
    }
    return render(request, 'explore/explore.html', context)


# -------------------------------------------------------------
# USER PROFILES & FOLLOW SYSTEM
# -------------------------------------------------------------

def profile_view(request, username):
    """User profile page with post grid/list, followers/following modals, and follow button."""
    target_user = get_object_or_404(User.objects.select_related('profile'), username=username)
    profile = target_user.profile

    tab = request.GET.get('tab', 'posts')  # 'posts', 'likes', 'media'

    if tab == 'likes':
        liked_post_ids = target_user.likes.values_list('post_id', flat=True)
        posts_qs = Post.objects.filter(id__in=liked_post_ids).select_related('author', 'author__profile')
    elif tab == 'media':
        posts_qs = target_user.posts.filter(image__isnull=False).exclude(image='').select_related('author', 'author__profile')
    else:
        posts_qs = target_user.posts.select_related('author', 'author__profile')

    paginator = Paginator(posts_qs, 9)
    page_number = request.GET.get('page', 1)
    posts = paginator.get_page(page_number)

    is_following = False
    if request.user.is_authenticated:
        is_following = profile.is_followed_by(request.user)
        user_liked_post_ids = set(Like.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True))
        for p in posts:
            p.has_liked = p.id in user_liked_post_ids

    context = {
        'target_user': target_user,
        'profile': profile,
        'posts': posts,
        'tab': tab,
        'is_following': is_following,
        'is_self': request.user == target_user,
    }
    return render(request, 'profile/profile.html', context)


@login_required
@require_POST
def follow_toggle_view(request, username):
    """Toggle follow/unfollow for a user."""
    target_user = get_object_or_404(User, username=username)
    current_user = request.user

    if target_user == current_user:
        return JsonResponse({'status': 'error', 'message': "You can't follow your iconic self!"}, status=400)

    follow_rel = Follow.objects.filter(follower=current_user, following=target_user).first()
    if follow_rel:
        follow_rel.delete()
        is_following = False
    else:
        Follow.objects.create(follower=current_user, following=target_user)
        is_following = True
        create_notification(
            recipient=target_user,
            actor=current_user,
            notification_type='follow'
        )

    followers_count = target_user.follower_set.count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'status': 'success',
            'is_following': is_following,
            'followers_count': followers_count
        })

    return redirect('profile', username=username)


def followers_list_view(request, username):
    """List followers for a user (modal or page view)."""
    target_user = get_object_or_404(User, username=username)
    followers = target_user.follower_set.select_related('follower', 'follower__profile').all()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [{
            'username': f.follower.username,
            'display_name': f.follower.profile.get_display_name(),
            'avatar': f.follower.profile.get_avatar_url(),
            'vibe_tag': f.follower.profile.vibe_tag,
            'is_following': f.follower.profile.is_followed_by(request.user) if request.user.is_authenticated else False
        } for f in followers]
        return JsonResponse({'followers': data})

    return render(request, 'profile/follow_list.html', {
        'target_user': target_user,
        'list_type': 'Followers',
        'relationships': followers,
        'is_followers': True
    })


def following_list_view(request, username):
    """List users followed by a user."""
    target_user = get_object_or_404(User, username=username)
    followings = target_user.following_set.select_related('following', 'following__profile').all()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [{
            'username': f.following.username,
            'display_name': f.following.profile.get_display_name(),
            'avatar': f.following.profile.get_avatar_url(),
            'vibe_tag': f.following.profile.vibe_tag,
            'is_following': f.following.profile.is_followed_by(request.user) if request.user.is_authenticated else False
        } for f in followings]
        return JsonResponse({'following': data})

    return render(request, 'profile/follow_list.html', {
        'target_user': target_user,
        'list_type': 'Following',
        'relationships': followings,
        'is_followers': False
    })


# -------------------------------------------------------------
# NOTIFICATIONS
# -------------------------------------------------------------

@login_required
def notifications_view(request):
    """Notifications page with unread highlighting and mark-as-read options."""
    notifs = request.user.notifications.select_related('actor', 'actor__profile', 'post').all()

    context = {
        'notifications': notifs,
    }
    return render(request, 'notifications/notifications.html', context)


@login_required
@require_POST
def mark_all_notifications_read_view(request):
    """Mark all notifications for current user as read."""
    request.user.notifications.filter(is_read=False).update(is_read=True)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'unread_count': 0})

    messages.success(request, "All notifications cleared! ✨")
    return redirect('notifications')


@login_required
@require_POST
def mark_single_notification_read_view(request, pk):
    """Mark individual notification as read."""
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    unread_count = request.user.notifications.filter(is_read=False).count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'unread_count': unread_count})

    if notif.post:
        return redirect('post_detail', pk=notif.post.pk)
    return redirect('profile', username=notif.actor.username)


# -------------------------------------------------------------
# SETTINGS & THEME TOGGLE
# -------------------------------------------------------------

@login_required
def settings_view(request):
    """User settings page to update profile, campus, interests, vibe tag, avatar, and theme."""
    profile = request.user.profile

    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        user_form = UserUpdateForm(request.POST, instance=request.user)

        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, "Vibe profile updated successfully! ✨")
            return redirect('settings')
        else:
            messages.error(request, "Could not update settings. Please check the fields below.")
    else:
        profile_form = ProfileUpdateForm(instance=profile)
        user_form = UserUpdateForm(instance=request.user)

    return render(request, 'settings/settings.html', {
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': profile
    })


@require_POST
def toggle_theme_view(request):
    """Toggle dark/light theme endpoint; updates profile if logged in and responds with new state."""
    try:
        body = json.loads(request.body.decode('utf-8'))
        theme = body.get('theme', 'dark')
    except Exception:
        theme = request.POST.get('theme', 'dark')

    if theme not in ['light', 'dark']:
        theme = 'dark'

    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        request.user.profile.theme_preference = theme
        request.user.profile.save()

    response = JsonResponse({'status': 'success', 'theme': theme})
    response.set_cookie('vibeup_theme', theme, max_age=365*24*60*60)
    return response
