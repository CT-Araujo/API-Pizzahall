# Generated by Django 4.2.7 on 2024-06-13 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_remove_produtos_preco_produtos_venda'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedidos',
            name='created',
            field=models.DateTimeField(auto_now=True),
        ),
    ]