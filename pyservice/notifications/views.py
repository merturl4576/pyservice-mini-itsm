"""
Notifications Views
PyService Mini-ITSM Platform
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def notification_list(request):
    """View all notifications."""
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications
    })


@login_required
def notification_api(request):
    """API endpoint for fetching notifications (for polling)."""
    notifications = Notification.get_recent_notifications(request.user, limit=10)
    unread_count = Notification.get_unread_count(request.user)
    
    data = {
        'unread_count': unread_count,
        'notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message[:100],
                'link': n.link,
                'is_read': n.is_read,
                'type': n.notification_type,
                'created_at': n.created_at.strftime('%b %d, %H:%M'),
            }
            for n in notifications
        ]
    }
    return JsonResponse(data)


@login_required
@require_POST
def mark_as_read(request, notification_id):
    """Mark a notification as read."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    return JsonResponse({'success': True})


@login_required
@require_POST
def mark_all_as_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})
