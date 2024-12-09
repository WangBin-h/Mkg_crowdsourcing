from django.db import models
from django.utils import timezone

class NormalUser(models.Model): #用户名称
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class asker(models.Model):
	
class expert(models.Model):
    