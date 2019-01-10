import pusher

from django.conf import settings


def pusher_notification(channel, event, data):
    pusher_client = pusher.Pusher(
        app_id=settings.PUSHER_APP_ID,
        key=settings.PUSHER_KEY,
        secret=settings.PUSHER_SECRET,
        cluster=settings.PUSHER_CLUSTER,
        ssl=True
    )
    pusher_client.trigger(channel, event, data)
