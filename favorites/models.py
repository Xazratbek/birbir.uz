from django.db import models
from utils.models import BaseModel
from accounts.models import User
from listings.models import Listing

class Favorite(BaseModel):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_favorites")
    favorite_listing = models.ForeignKey(Listing, on_delete=models.CASCADE,related_name="listing_favorites",null=True,blank=True)

    def __str__(self):
        return f"Foydalanuvchi: {self.user.username}-ning, sevimli e'loni: {self.favorite_listing.title}"

    class Meta:
        db_table = "favorites"
        verbose_name = "Saqlangan"
        verbose_name_plural = "Saqlanganlar"
        constraints = [
            models.UniqueConstraint(
                fields=["user","favorite_listing"], name='unique_user_favorite_listing'
            )
        ]