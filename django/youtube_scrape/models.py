from django.db import models
import datetime
import os


def getFileName(request,filename):
    now_time = datetime.datetime.now().strftime("%y%m%d%H:%M:%S")
    new_filename = "%s%s"%(now_time,filename)
    return os.path.join('uploads/',new_filename)  

from django.db import models

class Youtube_Data(models.Model):
    id = models.AutoField(primary_key=True)
    video_id = models.CharField(max_length=50,null=True)
    channel_title = models.CharField(max_length=255,null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    tags = models.TextField(null=True)
    published_at = models.DateTimeField(null=True)
    thumbnail = models.URLField(null=True)
    channel_id = models.TextField(null=True)
    view_count = models.IntegerField(null=True)
    like_count = models.IntegerField(null=True)
    comment_count = models.IntegerField(null=True)
    favorite_count = models.IntegerField(null=True)
    duration = models.TextField(null=True)
    definition = models.TextField(null=True)
    caption = models.TextField(null=True)

    def __str__(self):
        return self.id

