from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_temple_rich_fields'),
    ]

    operations = [
        # ── Mountain / Hill ─────────────────────────────────────────
        migrations.AddField(
            model_name='temple',
            name='altitude',
            field=models.CharField(max_length=100, blank=True, default='',
                                   help_text='[Mountain] Elevation (e.g. 2695 m)'),
        ),
        migrations.AddField(
            model_name='temple',
            name='trek_difficulty',
            field=models.CharField(
                max_length=20, blank=True, default='',
                choices=[('easy','Easy'),('moderate','Moderate'),('hard','Hard'),('extreme','Extreme')],
                help_text='[Mountain] Trek difficulty level'
            ),
        ),
        migrations.AddField(
            model_name='temple',
            name='trek_duration',
            field=models.CharField(max_length=100, blank=True, default='',
                                   help_text='[Mountain] Trek duration (e.g. 2–3 days)'),
        ),
        migrations.AddField(
            model_name='temple',
            name='viewpoints',
            field=models.TextField(blank=True, default='',
                                   help_text='[Mountain] Notable viewpoints or peaks'),
        ),
        migrations.AddField(
            model_name='temple',
            name='flora_fauna',
            field=models.TextField(blank=True, default='',
                                   help_text='[Mountain/Scenic] Wildlife and plant life found here'),
        ),

        # ── Beach / Coastal ─────────────────────────────────────────
        migrations.AddField(
            model_name='temple',
            name='beach_type',
            field=models.CharField(max_length=100, blank=True, default='',
                                   help_text='[Beach] Type (e.g. Sandy, Rocky, Black sand)'),
        ),
        migrations.AddField(
            model_name='temple',
            name='water_activity',
            field=models.TextField(blank=True, default='',
                                   help_text='[Beach] Activities (e.g. Surfing, Snorkelling, Swimming)'),
        ),
        migrations.AddField(
            model_name='temple',
            name='tide_info',
            field=models.CharField(max_length=200, blank=True, default='',
                                   help_text='[Beach] Tide pattern or swimming safety'),
        ),
        migrations.AddField(
            model_name='temple',
            name='nearby_stays',
            field=models.TextField(blank=True, default='',
                                   help_text='[Beach] Nearby accommodation options'),
        ),
        migrations.AddField(
            model_name='temple',
            name='sunset_sunrise',
            field=models.CharField(
                max_length=20, blank=True, default='',
                choices=[('sunrise','Sunrise Point'),('sunset','Sunset Point'),('both','Both'),('neither','Neither')],
                help_text='[Beach/Scenic] Famous for sunrise / sunset?'
            ),
        ),

        # ── Scenic / Nature ─────────────────────────────────────────
        migrations.AddField(
            model_name='temple',
            name='landscape_type',
            field=models.CharField(max_length=200, blank=True, default='',
                                   help_text='[Scenic] Landscape type (e.g. Waterfall, Forest, Valley)'),
        ),
        migrations.AddField(
            model_name='temple',
            name='wildlife',
            field=models.TextField(blank=True, default='',
                                   help_text='[Scenic] Notable wildlife or birds spotted here'),
        ),
        migrations.AddField(
            model_name='temple',
            name='entry_info',
            field=models.CharField(max_length=200, blank=True, default='',
                                   help_text='[Scenic] Entry fee / permit details'),
        ),
    ]
