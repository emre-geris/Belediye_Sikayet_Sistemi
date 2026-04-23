from .models import Notification


def create_status_notification(complaint, old_status, new_status):
    """Şikayet sahibine durum değişikliği bildirimi üret."""
    if not complaint.user or old_status == new_status:
        return

    Notification.objects.create(
        user=complaint.user,
        complaint=complaint,
        notification_type='status_update',
        title='Şikayet durumunuz güncellendi',
        message=(
            f'"{complaint.title}" başlıklı şikayetinizin durumu '
            f'"{old_status}" konumundan "{new_status}" durumuna geçirildi.'
        ),
    )
