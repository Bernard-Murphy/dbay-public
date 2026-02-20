from django.db import models
from django_ltree.fields import PathField

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    path = PathField(unique=True)
    icon_url = models.URLField(blank=True, null=True)
    sort_order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['path']

    def __str__(self):
        return self.name
