# Generated by Django 4.2 on 2023-05-02 12:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("youtube_scrape", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Channel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("channelTitle", models.CharField(max_length=255)),
                ("title", models.IntegerField()),
                ("description", models.IntegerField()),
                ("tags", models.IntegerField()),
                ("publishedAt", models.CharField(max_length=255)),
                ("thumbnail", models.CharField(max_length=255)),
                ("channelId", models.CharField(max_length=255)),
                ("viewCount", models.IntegerField()),
                ("likeCount", models.IntegerField()),
                ("commentCount", models.IntegerField()),
                ("favoriteCount", models.IntegerField()),
                ("duration", models.TextField(max_length=200)),
                ("definition", models.TextField(max_length=200)),
                ("caption", models.TextField(max_length=200)),
            ],
        ),
        migrations.DeleteModel(
            name="input",
        ),
    ]
