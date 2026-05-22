from django.db import models
from utils.models import BaseModel
from django.utils.text import slugify

class Category(BaseModel):
    name = models.CharField(max_length=100, db_index=True,verbose_name="Kategoriya")
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey("self", null=True, related_name="categories", blank=True,on_delete=models.CASCADE)
    icon = models.ImageField(upload_to="category_icons/%Y/%m/%d/",null=True,blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "categories"
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"