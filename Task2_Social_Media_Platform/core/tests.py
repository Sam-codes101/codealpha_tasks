from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Profile, Post, Comment, Like, Follow, Notification


class AuthAndProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='testuser1', email='test1@campus.edu', password='Password123!')
        self.user2 = User.objects.create_user(username='testuser2', email='test2@campus.edu', password='Password123!')

    def test_profile_auto_created_on_user_creation(self):
        """Profile should be created automatically via signal."""
        self.assertTrue(hasattr(self.user1, 'profile'))
        self.assertEqual(self.user1.profile.user, self.user1)
        self.assertTrue(len(self.user1.profile.get_avatar_url()) > 0)

    def test_user_signup(self):
        """Test registration flow with valid credentials."""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'new@campus.edu',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)  # Redirects to home
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_password_mismatch(self):
        """Test registration rejects mismatched passwords."""
        response = self.client.post(reverse('signup'), {
            'username': 'mismatchuser',
            'email': 'mismatch@campus.edu',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='mismatchuser').exists())

    def test_user_login_and_logout(self):
        """Test login and logout flow."""
        login_success = self.client.login(username='testuser1', password='Password123!')
        self.assertTrue(login_success)

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        logout_response = self.client.get(reverse('logout'))
        self.assertEqual(logout_response.status_code, 302)
        self.assertRedirects(logout_response, reverse('landing'))

    def test_profile_update(self):
        """Profile owner can update display name, bio, campus, and interests."""
        self.client.login(username='testuser1', password='Password123!')
        response = self.client.post(reverse('settings'), {
            'display_name': 'Test Creator ✨',
            'bio': 'Campus photographer & caffeine enthusiast.',
            'pronouns': 'they/them',
            'campus': "NYU '26",
            'vibe_tag': 'Matcha Fiend',
            'interests': 'Photography, Film, Lo-Fi',
            'website': 'https://vibeup.xyz',
            'theme_preference': 'light',
            'email': 'updated@campus.edu'
        })
        self.assertEqual(response.status_code, 302)

        self.user1.profile.refresh_from_db()
        self.assertEqual(self.user1.profile.display_name, 'Test Creator ✨')
        self.assertEqual(self.user1.profile.campus, "NYU '26")
        self.assertEqual(self.user1.profile.theme_preference, 'light')
        self.assertEqual(len(self.user1.profile.get_interests_list()), 3)


class PostAndFeedTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='Password123!')
        self.user2 = User.objects.create_user(username='user2', password='Password123!')

    def test_create_post_authenticated(self):
        """Authenticated user can create a post."""
        self.client.login(username='user1', password='Password123!')
        response = self.client.post(reverse('create_post'), {
            'content': 'Late night campus coding session #midnightsesh #coding',
            'mood': '🎧 In My Zone'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.author, self.user1)
        self.assertIn('midnightsesh', post.extract_hashtags())

    def test_empty_post_validation(self):
        """Empty post is rejected."""
        self.client.login(username='user1', password='Password123!')
        response = self.client.post(reverse('create_post'), {
            'content': '   ',
            'mood': ''
        })
        self.assertEqual(Post.objects.count(), 0)

    def test_unauthenticated_cannot_post(self):
        """Unauthenticated user cannot create post and is redirected."""
        response = self.client.post(reverse('create_post'), {'content': 'Hacked post'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
        self.assertEqual(Post.objects.count(), 0)

    def test_post_edit_by_author(self):
        """Author can edit their own post."""
        post = Post.objects.create(author=self.user1, content='Original content')
        self.client.login(username='user1', password='Password123!')

        response = self.client.post(reverse('edit_post', kwargs={'pk': post.pk}), {
            'content': 'Updated content with new vibes',
            'mood': '✨ Feeling Iconic'
        })
        self.assertEqual(response.status_code, 302)
        post.refresh_from_db()
        self.assertEqual(post.content, 'Updated content with new vibes')
        self.assertEqual(post.mood, '✨ Feeling Iconic')

    def test_post_edit_by_unauthorized_user_forbidden(self):
        """Non-author cannot edit someone else's post."""
        post = Post.objects.create(author=self.user1, content='User1 post')
        self.client.login(username='user2', password='Password123!')

        response = self.client.post(reverse('edit_post', kwargs={'pk': post.pk}), {
            'content': 'Attempted hijack'
        })
        self.assertEqual(response.status_code, 403)
        post.refresh_from_db()
        self.assertEqual(post.content, 'User1 post')

    def test_post_delete_by_author(self):
        """Author can delete their own post."""
        post = Post.objects.create(author=self.user1, content='To be deleted')
        self.client.login(username='user1', password='Password123!')

        response = self.client.post(reverse('delete_post', kwargs={'pk': post.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.filter(pk=post.pk).count(), 0)

    def test_home_feed_filters_followed_users(self):
        """Home feed 'following' tab shows followed user's posts, not unfollowed."""
        user3 = User.objects.create_user(username='user3', password='Password123!')
        Follow.objects.create(follower=self.user1, following=self.user2)

        post_followed = Post.objects.create(author=self.user2, content='Post from followed user')
        post_unfollowed = Post.objects.create(author=user3, content='Post from unfollowed user')

        self.client.login(username='user1', password='Password123!')
        response = self.client.get(reverse('home') + '?feed=following')

        posts_in_feed = response.context['posts'].object_list
        self.assertIn(post_followed, posts_in_feed)
        self.assertNotIn(post_unfollowed, posts_in_feed)


class LikeAndCommentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='Password123!')
        self.user2 = User.objects.create_user(username='user2', password='Password123!')
        self.post = Post.objects.create(author=self.user1, content='Test post for likes and comments')

    def test_like_toggle_and_notification(self):
        """User2 likes post -> Like created, count increases, notification sent to post author."""
        self.client.login(username='user2', password='Password123!')

        # First like
        response = self.client.post(reverse('like_toggle', kwargs={'pk': self.post.pk}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['liked'])
        self.assertEqual(data['likes_count'], 1)
        self.assertEqual(self.post.likes.count(), 1)

        # Check notification sent to user1
        self.assertTrue(Notification.objects.filter(recipient=self.user1, actor=self.user2, notification_type='like').exists())

        # Unlike
        response2 = self.client.post(reverse('like_toggle', kwargs={'pk': self.post.pk}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data2 = response2.json()
        self.assertFalse(data2['liked'])
        self.assertEqual(data2['likes_count'], 0)
        self.assertEqual(self.post.likes.count(), 0)

    def test_no_self_notification_on_like(self):
        """Liking own post does not generate a notification."""
        self.client.login(username='user1', password='Password123!')
        self.client.post(reverse('like_toggle', kwargs={'pk': self.post.pk}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertFalse(Notification.objects.filter(recipient=self.user1, actor=self.user1).exists())

    def test_add_and_delete_comment(self):
        """User can add comment and comment author can delete it."""
        self.client.login(username='user2', password='Password123!')

        # Add comment
        response = self.client.post(reverse('add_comment', kwargs={'pk': self.post.pk}), {
            'content': 'Iconic vibe honestly ✨'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.post.comments.count(), 1)
        comment = self.post.comments.first()
        self.assertEqual(comment.author, self.user2)

        # Delete comment
        del_response = self.client.post(reverse('delete_comment', kwargs={'pk': comment.pk}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(del_response.status_code, 200)
        self.assertEqual(self.post.comments.count(), 0)


class FollowAndExploreTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='Password123!')
        self.user2 = User.objects.create_user(username='user2', password='Password123!')

    def test_follow_toggle(self):
        """Follow and unfollow flow."""
        self.client.login(username='user1', password='Password123!')

        # Follow
        res = self.client.post(reverse('follow_toggle', kwargs={'username': self.user2.username}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['is_following'])
        self.assertEqual(self.user2.profile.followers_count, 1)
        self.assertEqual(self.user1.profile.following_count, 1)

        # Notification sent to user2
        self.assertTrue(Notification.objects.filter(recipient=self.user2, actor=self.user1, notification_type='follow').exists())

        # Unfollow
        res2 = self.client.post(reverse('follow_toggle', kwargs={'username': self.user2.username}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res2.status_code, 200)
        self.assertFalse(res2.json()['is_following'])
        self.assertEqual(self.user2.profile.followers_count, 0)

    def test_cannot_follow_self(self):
        """User cannot follow themselves."""
        self.client.login(username='user1', password='Password123!')
        res = self.client.post(reverse('follow_toggle', kwargs={'username': self.user1.username}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(Follow.objects.count(), 0)

    def test_explore_search_records(self):
        """Explore search returns real database matches for users and posts."""
        Post.objects.create(author=self.user1, content='Amazing matcha latte at library')
        Post.objects.create(author=self.user2, content='Studio photography session')

        # Search for 'matcha'
        res = self.client.get(reverse('explore') + '?q=matcha')
        self.assertEqual(res.status_code, 200)
        posts = res.context['posts'].object_list
        self.assertEqual(len(posts), 1)
        self.assertIn('matcha', posts[0].content)

        # Search for user handle
        res_user = self.client.get(reverse('explore') + '?q=user2')
        matching_users = res_user.context['matching_users']
        self.assertIn(self.user2, matching_users)


class NotificationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='Password123!')
        self.user2 = User.objects.create_user(username='user2', password='Password123!')

    def test_notifications_page_and_mark_all_read(self):
        """Test unread badge and marking all as read."""
        Notification.objects.create(recipient=self.user1, actor=self.user2, notification_type='follow')
        Notification.objects.create(recipient=self.user1, actor=self.user2, notification_type='like')

        self.client.login(username='user1', password='Password123!')
        res = self.client.get(reverse('notifications'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['unread_notifications_count'], 2)

        # Mark all read
        mark_res = self.client.post(reverse('mark_all_notifications_read'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(mark_res.status_code, 200)
        self.assertEqual(self.user1.notifications.filter(is_read=False).count(), 0)
