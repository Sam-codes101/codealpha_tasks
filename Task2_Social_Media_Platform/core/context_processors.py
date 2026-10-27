def vibeup_context(request):
    """Global context processor for VIBEUP."""
    context = {
        'APP_NAME': 'VIBEUP',
        'APP_TAGLINE': 'Your people. Your chaos. Your corner of the internet.',
        'unread_notifications_count': 0,
        'user_theme': 'dark',
    }

    if request.user.is_authenticated:
        # Check unread notifications count
        try:
            context['unread_notifications_count'] = request.user.notifications.filter(is_read=False).count()
        except Exception:
            context['unread_notifications_count'] = 0

        # Get profile theme preference
        try:
            if hasattr(request.user, 'profile'):
                context['user_theme'] = request.user.profile.theme_preference or 'dark'
        except Exception:
            pass

    return context
