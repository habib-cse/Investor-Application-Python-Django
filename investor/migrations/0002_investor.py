# Generated by Django 3.0.7 on 2020-06-16 06:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Investor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150)),
                ('password', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=13)),
                ('address', models.TextField()),
                ('account_number', models.IntegerField()),
                ('agree_to_invest', models.BooleanField(default=True)),
                ('status', models.BooleanField(default=False)),
                ('bank_name', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='investor.Bank')),
            ],
            options={
                'verbose_name': 'Investor',
                'verbose_name_plural': 'Investors',
            },
        ),
    ]
