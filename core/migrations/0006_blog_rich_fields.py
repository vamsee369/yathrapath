from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_temple_category_fields'),
    ]

    operations = [
        # ── Stats ────────────────────────────────────────────────────
        migrations.AddField(
            model_name='blog',
            name='views',
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='blog',
            name='reading_time',
            field=models.PositiveIntegerField(default=0, editable=False,
                                              help_text='Auto-calculated in minutes'),
        ),

        # ── Rich content fields ──────────────────────────────────────
        migrations.AddField(
            model_name='blog',
            name='intro',
            field=models.TextField(blank=True, default='',
                                   help_text='Opening hook — why you went, what drew you there'),
        ),
        migrations.AddField(
            model_name='blog',
            name='experience',
            field=models.TextField(blank=True, default='',
                                   help_text='The main story — what you saw, felt, and did'),
        ),
        migrations.AddField(
            model_name='blog',
            name='highlights',
            field=models.TextField(blank=True, default='',
                                   help_text='Best moments (pipe-separated: Title:Description|Title:Description)'),
        ),
        migrations.AddField(
            model_name='blog',
            name='travel_tips',
            field=models.TextField(blank=True, default='',
                                   help_text='Practical tips for readers planning a visit'),
        ),
        migrations.AddField(
            model_name='blog',
            name='best_time',
            field=models.CharField(max_length=200, blank=True, default='',
                                   help_text='Best time / season to visit'),
        ),
        migrations.AddField(
            model_name='blog',
            name='how_to_reach',
            field=models.TextField(blank=True, default='',
                                   help_text='How to get there — transport, routes, distance'),
        ),
        migrations.AddField(
            model_name='blog',
            name='food_stay',
            field=models.TextField(blank=True, default='',
                                   help_text='Where to eat and stay nearby'),
        ),
        migrations.AddField(
            model_name='blog',
            name='closing_thought',
            field=models.TextField(blank=True, default='',
                                   help_text='Final reflection or poetic closing line'),
        ),
        migrations.AddField(
            model_name='blog',
            name='image_caption',
            field=models.CharField(max_length=200, blank=True, default='',
                                   help_text='Caption shown below the cover image'),
        ),
    ]
