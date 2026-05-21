from django.db import models


# Create your models here.
class StoreModels(models.Model):
    cnpj = models.CharField(max_length=14)
    razao_social = models.CharField(max_length=100)
    email = models.EmailField()
    senha = models.CharField(max_length=256)
