# Generated by Django 3.0.7 on 2020-07-11 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investor', '0035_auto_20200710_0621'),
    ]

    operations = [
        migrations.CreateModel(
            name='Access',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('has_access', models.CharField(max_length=300)),
                ('status', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_name', models.CharField(max_length=200)),
                ('access', models.ManyToManyField(to='investor.Access')),
            ],
        ),
    ]
