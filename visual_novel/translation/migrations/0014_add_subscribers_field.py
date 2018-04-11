# Generated by Django 2.0.2 on 2018-04-11 14:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_add_subscribers_field'),
        ('translation', '0013_add_moderator_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='TranslationSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Profile')),
                ('translation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations_set', to='translation.TranslationItem')),
            ],
            options={
                'verbose_name': 'Подписка на рассылку',
                'verbose_name_plural': 'Подписки',
                'db_table': 'translation_subscriptions',
            },
        ),
        migrations.AddField(
            model_name='translationitem',
            name='subscriber',
            field=models.ManyToManyField(blank=True, through='translation.TranslationSubscription', to='core.Profile', verbose_name='Подписчики'),
        ),
    ]
