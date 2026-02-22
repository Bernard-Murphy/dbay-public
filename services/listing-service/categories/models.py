from django.db import models
from django_ltree.fields import PathField


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    path = PathField(unique=True)
    icon_url = models.URLField(blank=True, null=True)
    default_icon = models.CharField(max_length=32, blank=True)  # e.g. "car", "soccer-ball" for Lucide
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["path"]

    def __str__(self):
        return self.name


class CategoryItem(models.Model):
    """Quick-search items under a category (e.g. Automobiles -> Tesla, Honda)."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, null=True)  # default picture for this item (placeholder)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["category", "sort_order", "name"]
        unique_together = [["category", "name"]]

    def __str__(self):
        return f"{self.category.name} > {self.name}"
