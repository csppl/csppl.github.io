# Generated by Django 2.2.2 on 2019-06-26 10:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.TextField()),
                ('size', models.TextField()),
                ('chart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boards.Chart')),
            ],
        ),
    ]
