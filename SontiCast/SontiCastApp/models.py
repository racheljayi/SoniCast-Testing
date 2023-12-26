from django.db import models

class User(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    user_spotify_id = models.CharField(max_length=50, unique=True)
    access_token = models.CharField(max_length=300, null=True)
    refresh_token = models.CharField(max_length=300, null=True)
    city = models.CharField(max_length=255, null=True)
    region = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    playlist_id = models.CharField(max_length=300, null=True)

    def __str__(self):
        return self.user_spotify_id