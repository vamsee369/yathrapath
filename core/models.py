from django.utils import timezone
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import json
import math


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

    CATEGORY_CHOICES = [
        ('temple',   'Temple / Religious'),
        ('mountain', 'Mountain / Hill'),
        ('beach',    'Beach / Coastal'),
        ('scenic',   'Scenic / Nature'),
        ('heritage', 'Heritage / Historical'),
        ('other',    'Other'),
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
    category    = models.CharField(
                    max_length=20,
                    choices=CATEGORY_CHOICES,
                    default='temple'
                  )

    # ── Shared fields (all categories) ─────────────────────────────
    best_season  = models.CharField(max_length=200, blank=True)
    timings      = models.CharField(max_length=200, blank=True, help_text="Opening hours / visit hours")
    mystery      = models.TextField(blank=True, help_text="Hidden mystery or unexplained fact")
    rare_fact    = models.TextField(blank=True, help_text="What most visitors never notice")
    quote        = models.TextField(blank=True, help_text="A poetic or powerful quote about this place")

    # ── Temple / Religious fields ───────────────────────────────────
    deity        = models.CharField(max_length=200, blank=True, help_text="[Temple] Main deity worshipped")
    dynasty      = models.CharField(max_length=200, blank=True, help_text="[Temple/Heritage] Built by dynasty or ruler")
    festivals    = models.TextField(blank=True, help_text="[Temple] Major festivals celebrated")
    history      = models.TextField(blank=True, help_text="[Temple/Heritage] Historical background")
    architecture = models.TextField(blank=True, help_text="[Temple/Heritage] Architectural style and features")
    rituals      = models.TextField(blank=True, help_text="[Temple] Rituals (pipe-separated: Title:Description|Title:Description)")
    science_fact = models.TextField(blank=True, help_text="[Temple/Heritage] Scientific or architectural wonder")

    # ── Mountain / Hill fields ──────────────────────────────────────
    altitude        = models.CharField(max_length=100, blank=True, help_text="[Mountain] Elevation (e.g. 2695 m)")
    trek_difficulty = models.CharField(
                        max_length=20,
                        blank=True,
                        choices=[
                            ('easy',    'Easy'),
                            ('moderate','Moderate'),
                            ('hard',    'Hard'),
                            ('extreme', 'Extreme'),
                        ],
                        help_text="[Mountain] Trek difficulty level"
                      )
    trek_duration   = models.CharField(max_length=100, blank=True, help_text="[Mountain] Trek duration (e.g. 2–3 days)")
    viewpoints      = models.TextField(blank=True, help_text="[Mountain] Notable viewpoints or peaks")
    flora_fauna     = models.TextField(blank=True, help_text="[Mountain/Scenic] Wildlife and plant life found here")

    # ── Beach / Coastal fields ──────────────────────────────────────
    beach_type     = models.CharField(max_length=100, blank=True, help_text="[Beach] Type (e.g. Sandy, Rocky, Black sand)")
    water_activity = models.TextField(blank=True, help_text="[Beach] Activities (e.g. Surfing, Snorkelling, Swimming)")
    tide_info      = models.CharField(max_length=200, blank=True, help_text="[Beach] Tide pattern or swimming safety")
    nearby_stays   = models.TextField(blank=True, help_text="[Beach] Nearby accommodation options")
    sunset_sunrise = models.CharField(
                        max_length=20,
                        blank=True,
                        choices=[
                            ('sunrise', 'Sunrise Point'),
                            ('sunset',  'Sunset Point'),
                            ('both',    'Both'),
                            ('neither', 'Neither'),
                        ],
                        help_text="[Beach/Scenic] Famous for sunrise / sunset?"
                      )

    # ── Scenic / Nature fields ──────────────────────────────────────
    landscape_type = models.CharField(max_length=200, blank=True, help_text="[Scenic] Landscape type (e.g. Waterfall, Forest, Valley)")
    wildlife       = models.TextField(blank=True, help_text="[Scenic] Notable wildlife or birds spotted here")
    entry_info     = models.CharField(max_length=200, blank=True, help_text="[Scenic] Entry fee / permit details")

    def __str__(self):
        return self.name


class Blog(models.Model):
    # ── Core ────────────────────────────────────────────────────────
    title      = models.CharField(max_length=200)
    image      = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    image_caption = models.CharField(max_length=200, blank=True, help_text="Caption shown below the cover image")
    created_at = models.DateTimeField(default=timezone.now)

    # ── Auto-managed stats ──────────────────────────────────────────
    views        = models.PositiveIntegerField(default=0, editable=False)
    reading_time = models.PositiveIntegerField(default=0, editable=False, help_text="Auto-calculated in minutes")

    # ── Legacy field — kept so old blogs don't break ────────────────
    content = models.TextField(blank=True, help_text="Legacy field — use the rich fields below for new posts")

    # ── Rich content fields ─────────────────────────────────────────
    intro           = models.TextField(blank=True, help_text="Opening hook — why you went, what drew you there")
    experience      = models.TextField(blank=True, help_text="The main story — what you saw, felt, and did")
    highlights      = models.TextField(blank=True, help_text="Best moments (pipe-separated: Title:Description|Title:Description)")
    travel_tips     = models.TextField(blank=True, help_text="Practical tips for readers planning a visit")
    best_time       = models.CharField(max_length=200, blank=True, help_text="Best time / season to visit")
    how_to_reach    = models.TextField(blank=True, help_text="How to get there — transport, routes, distance")
    food_stay       = models.TextField(blank=True, help_text="Where to eat and stay nearby")
    closing_thought = models.TextField(blank=True, help_text="Final reflection or poetic closing line")

    def _all_text(self):
        parts = [
            self.content, self.intro, self.experience,
            self.highlights, self.travel_tips, self.how_to_reach,
            self.food_stay, self.closing_thought,
        ]
        return ' '.join(p for p in parts if p)

    def calculate_reading_time(self):
        words = len(self._all_text().split())
        return max(1, math.ceil(words / 200))

    def save(self, *args, **kwargs):
        self.reading_time = self.calculate_reading_time()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PushSubscription(models.Model):
    endpoint   = models.TextField(unique=True)
    p256dh     = models.TextField()
    auth       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.endpoint[:60]


# ── Signals ───────────────────────────────────────────────────────────────────

STATUS_EMOJI = {
    'completed':   '✅',
    'planned':     '🔵',
    'not_visited': '🔴',
}

STATUS_LABEL = {
    'completed':   'Visited',
    'planned':     'Planned',
    'not_visited': 'Not Visited',
}


@receiver(post_save, sender=Temple)
def temple_notification(sender, instance, created, **kwargs):
    if created:
        _send_to_all({
            "title": "New Destination Added 🛕",
            "body": f"{instance.name}, {instance.location} is now on YatraPath!",
            "url": f"/temple/{instance.id}/"
        })
    else:
        old_status = getattr(instance, '_original_status', None)
        if old_status and old_status != instance.status:
            emoji = STATUS_EMOJI.get(instance.status, '')
            label = STATUS_LABEL.get(instance.status, instance.status)
            _send_to_all({
                "title": f"Status Updated {emoji}",
                "body": f"{instance.name} is now marked as {label}.",
                "url": f"/temple/{instance.id}/"
            })


@receiver(post_save, sender=Blog)
def blog_notification(sender, instance, created, **kwargs):
    if created:
        _send_to_all({
            "title": "New Blog Post 📖",
            "body": f"{instance.title} — read it now on YatraPath!",
            "url": f"/blog/{instance.id}/"
        })
