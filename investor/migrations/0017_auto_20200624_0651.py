# Generated by Django 3.0.7 on 2020-06-24 06:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('investor', '0016_delete_pdfsignimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='message')),
            ],
        ),
        migrations.AlterField(
            model_name='investor',
            name='status',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('is_admin', models.BooleanField(default=False)),
                ('status', models.BooleanField(default=True)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('attachment', models.ManyToManyField(to='investor.Attachment')),
                ('investor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='investor.Investor')),
            ],
        ),
    ]
