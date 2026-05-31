from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('core', '0003_temple_category')]
    operations = [
        migrations.AddField(model_name='temple', name='deity',        field=models.CharField(max_length=200, blank=True, default='')),
        migrations.AddField(model_name='temple', name='dynasty',      field=models.CharField(max_length=200, blank=True, default='')),
        migrations.AddField(model_name='temple', name='timings',      field=models.CharField(max_length=200, blank=True, default='')),
        migrations.AddField(model_name='temple', name='best_season',  field=models.CharField(max_length=200, blank=True, default='')),
        migrations.AddField(model_name='temple', name='festivals',    field=models.TextField(blank=True, default='')),
        migrations.AddField(model_name='temple', name='history',      field=models.TextField(blank=True, default='')),
        migrations.AddField(model_name='temple', name='architecture', field=models.TextField(blank=True, default='')),
        migrations.AddField(model_name='temple', name='rituals',      field=models.TextField(blank=True, default='')),
        migrations.AddField(model_name='temple', name='science_fact', field=models.TextField(blank=True, default='')),
        migrations.AddField(model_name='temple', name='mystery',      field=models.TextField(blank=True, default='')),
        migrations.AddField(model_name='temple', name='rare_fact',    field=models.TextField(blank=True, default='')),
        migrations.AddField(model_name='temple', name='quote',        field=models.TextField(blank=True, default='')),
    ]
