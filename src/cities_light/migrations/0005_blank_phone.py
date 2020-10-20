from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cities_light', '0004_autoslug_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='phone',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
