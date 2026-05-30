"""
Fires push notifications to all subscribers when a new Temple or Blog is created.
Requires pywebpush: pip install pywebpush
"""
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import Temple, Blog, PushSubscription


def _send_push(title: str, body: str, url: str = "/"):
    """Send a push notification to every subscriber (best-effort)."""
    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        return  # pywebpush not installed — skip silently

    payload = json.dumps({"title": title, "body": body, "url": url})
    private_key = getattr(settings, 'VAPID_PRIVATE_KEY', '')
    claims = getattr(settings, 'VAPID_CLAIMS', {})

    if not private_key:
        return  # VAPID not configured

    for sub in PushSubscription.objects.all():
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                },
                data=payload,
                vapid_private_key=private_key,
                vapid_claims=claims,
            )
        except Exception:
            sub.delete()  # Remove dead subscription


@receiver(post_save, sender=Temple)
def notify_new_temple(sender, instance, created, **kwargs):
    if created:
        _send_push(
            title="✨ New Temple Added – YatraPath",
            body=f"{instance.name} has been added to Destinations!",
            url="/temples/",
        )


@receiver(post_save, sender=Blog)
def notify_new_blog(sender, instance, created, **kwargs):
    if created:
        _send_push(
            title="📖 New Blog Post – YatraPath",
            body=f'"{instance.title}" is now live on YatraPath Blog.',
            url="/blog/",
        )
