"""
Context Processors
PyService Mini-ITSM Platform
"""

def notifications_context(request):
    """Add notification data to all templates."""
    if request.user.is_authenticated:
        from notifications.models import Notification
        return {
            'unread_notifications_count': Notification.get_unread_count(request.user),
            'recent_notifications': Notification.get_recent_notifications(request.user, limit=5),
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': [],
    }
