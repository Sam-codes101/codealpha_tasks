from django.urls import path
from . import views

urlpatterns = [
    # Auth & Landing
    path('', views.landing_view, name='landing'),
    path('feed/', views.home_feed_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Posts
    path('post/create/', views.create_post_view, name='create_post'),
    path('post/<int:pk>/', views.post_detail_view, name='post_detail'),
    path('post/<int:pk>/edit/', views.edit_post_view, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post_view, name='delete_post'),
    path('post/<int:pk>/like/', views.like_toggle_view, name='like_toggle'),
    path('post/<int:pk>/comment/', views.add_comment_view, name='add_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment_view, name='delete_comment'),

    # Explore
    path('explore/', views.explore_view, name='explore'),

    # Profiles & Relationships
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/<str:username>/follow/', views.follow_toggle_view, name='follow_toggle'),
    path('profile/<str:username>/followers/', views.followers_list_view, name='user_followers'),
    path('profile/<str:username>/following/', views.following_list_view, name='user_following'),

    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/read-all/', views.mark_all_notifications_read_view, name='mark_all_notifications_read'),
    path('notifications/<int:pk>/read/', views.mark_single_notification_read_view, name='mark_single_notification_read'),

    # Settings & Preferences
    path('settings/', views.settings_view, name='settings'),
    path('api/toggle-theme/', views.toggle_theme_view, name='toggle_theme'),
]
