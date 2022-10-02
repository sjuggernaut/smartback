# Generated by Django 3.2 on 2022-09-24 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calibration', '0008_calibrationstep'),
    ]

    operations = [
        migrations.AddField(
            model_name='calibration',
            name='status',
            field=models.CharField(choices=[('CREATED', 'Created'), ('COMPLETED', 'Completed'), ('STARTED', 'Started'), ('FAILED', 'Failed')], default=('CREATED', 'Created'), max_length=256),
        ),
    ]
