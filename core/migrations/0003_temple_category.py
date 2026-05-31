from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_pushsubscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='temple',
            name='category',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('temple',   'Temple / Religious'),
                    ('mountain', 'Mountain / Hill'),
                    ('beach',    'Beach / Coastal'),
                    ('scenic',   'Scenic / Nature'),
                    ('heritage', 'Heritage / Historical'),
                    ('other',    'Other'),
                ],
                default='temple',
            ),
        ),
    ]
