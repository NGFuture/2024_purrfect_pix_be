from django.db import models

# Create your models here.
class Breed(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    temperament = models.CharField(max_length=255)
    origin = models.CharField(max_length=255)
    description = models.TextField()
    life_span = models.CharField(max_length=255)

class Cat(models.Model):
    breeds = models.ManyToManyField(Breed)
    id = models.CharField(max_length=255, primary_key=True)
    url = models.URLField()
    width = models.IntegerField()
    height = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField()
    favorite = models.BooleanField(default=False)
