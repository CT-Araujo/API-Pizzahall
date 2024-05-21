# Generated by Django 4.2.7 on 2024-05-05 18:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_user_googleid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pizzarias',
            fields=[
                ('id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('name', models.CharField(max_length=50)),
                ('status', models.CharField(default='Fechado', max_length=20)),
                ('telefone', models.CharField(max_length=11)),
                ('cnpj', models.CharField(blank=True, default=None, max_length=14, unique=True)),
                ('horario', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='cliente',
            name='cpf',
            field=models.CharField(blank=True, default=None, max_length=14, unique=True),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='telefone',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
    ]
