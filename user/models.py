from django.db import models

# Create your models here.

class User(models.Model):

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.nick_name

    openid = models.CharField(max_length=50, primary_key=True)
    nick_name = models.CharField(max_length=100, null=True, blank=True)
    avatar_url = models.URLField(null=True, blank=True)
    reg_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
