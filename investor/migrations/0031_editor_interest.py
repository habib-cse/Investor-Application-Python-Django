# Generated by Django 3.0.7 on 2020-07-09 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investor', '0030_auto_20200705_1247'),
    ]

    operations = [
        migrations.CreateModel(
            name='Editor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150)),
                ('full_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=100)),
                ('status', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Editor',
                'verbose_name_plural': 'Editors',
            },
        ),
        migrations.CreateModel(
            name='Interest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Editor',
                'verbose_name_plural': 'Editors',
            },
        ),
    ]
