from django.utils import timezone
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import json


# ── Helper: send to all subscribers ──────────────────────────────────────────

def _send_to_all(payload):
    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        return

    for sub in PushSubscription.objects.all():
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth}
                },
                data=json.dumps(payload),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims=settings.VAPID_CLAIMS,
                headers={
                    "Urgency": "high",
                    "TTL": "86400",
                }
            )
        except WebPushException as e:
            print(f"[Push] Failed for {sub.endpoint[:40]}… → {e}")
            sub.delete()
        except Exception as e:
            print(f"[Push] Unexpected error → {e}")
            sub.delete()


# ── Models ────────────────────────────────────────────────────────────────────

class Temple(models.Model):

    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('planned', 'Planned'),
        ('not_visited', 'Not Visited'),
    ]

    name        = models.CharField(max_length=200)
    location    = models.CharField(max_length=200)
    description = models.TextField()
    image       = models.ImageField(upload_to='temples/')
    latitude    = models.FloatField()
    longitude   = models.FloatField()
    status      = models.CharField(
                    max_length=20,
                    choices=STATUS_CHOICES,
                    default='not_visited'
                  )

    def __str__(self):
        return self.name


class Blog(models.Model):
    title      = models.CharField(max_length=200)
    content    = models.TextField()
    image      = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class PushSubscription(models.Model):
    endpoint  = models.TextField(unique=True)
    p256dh    = models.TextField()
    auth      = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.endpoint[:60]


# ── Signals ───────────────────────────────────────────────────────────────────

STATUS_EMOJI = {
    'completed':  '✅',
    'planned':    '🔵',
    'not_visited': '🔴',
}

STATUS_LABEL = {
    'completed':  'Visited',
    'planned':    'Planned',
    'not_visited': 'Not Visited',
}


@receiver(post_save, sender=Temple)
def temple_notification(sender, instance, created, **kwargs):
    if created:
        # New temple added
        _send_to_all({
            "title": "New Destination Added 🛕",
            "body": f"{instance.name}, {instance.location} is now on YatraPath!",
            "url": f"/temple/{instance.id}/"   # was /temples/
        })
    else:
        # Check if status changed — compare with DB value before save
        try:
            old = Temple.objects.get(pk=instance.pk)
        except Temple.DoesNotExist:
            return

        # post_save fires after save so we track old value via __original_status
        old_status = getattr(instance, '_original_status', None)
        if old_status and old_status != instance.status:
            emoji = STATUS_EMOJI.get(instance.status, '')
            label = STATUS_LABEL.get(instance.status, instance.status)
            _send_to_all({
                "title": f"Status Updated {emoji}",
                "body": f"{instance.name} is now marked as {label}.",
                "url": f"/temple/{instance.id}/"   # was /temples/
            })


@receiver(post_save, sender=Blog)
def blog_notification(sender, instance, created, **kwargs):
    if created:
        _send_to_all({
            "title": "New Blog Post 📖",
            "body": f"{instance.title} — read it now on YatraPath!",
            "url": f"/blog/{instance.id}/"     # was /blog/
        })