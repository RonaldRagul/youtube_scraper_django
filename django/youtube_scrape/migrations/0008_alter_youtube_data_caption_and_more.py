# Generated by Django 4.2 on 2023-05-03 10:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("youtube_scrape", "0007_alter_youtube_data_caption_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="youtube_data",
            name="caption",
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="youtube_data",
            name="channel_id",
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="youtube_data",
            name="definition",
            field=models.TextField(),
        ),
    ]
