# Generated by Django 4.2.7 on 2024-05-05 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_pizzarias_alter_cliente_cpf_alter_cliente_telefone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='cpf',
            field=models.CharField(blank=True, default=None, max_length=14, null=True, unique=True),
        ),
    ]
