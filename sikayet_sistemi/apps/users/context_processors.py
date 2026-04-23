from .models import Notification


def notification_context(request):
    """Topbar bildirim verilerini tüm şablonlara taşır."""
    if not request.user.is_authenticated:
        return {
            'header_notifications': [],
            'header_unread_notifications_count': 0,
        }

    notifications = Notification.objects.filter(user=request.user).select_related('complaint')[:8]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return {
        'header_notifications': notifications,
        'header_unread_notifications_count': unread_count,
    }
