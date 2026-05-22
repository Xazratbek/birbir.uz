from django.db import models
from utils.models import BaseModel
from accounts.models import User
from listings.models import Listing

class ChatRoom(BaseModel):
    chat_listing = models.ForeignKey(Listing, on_delete=models.SET_NULL,related_name='listing_chatrooms',db_index=True, null=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_chatrooms',db_index=True)
    seller = models.ForeignKey(User,on_delete=models.CASCADE, related_name="seller_chatrooms",db_index=True)

    def __str__(self):
        return f"Room name: {self.chat_listing.title} | Buyer: {self.buyer.username} | Seller: {self.seller.username}"

    class Meta:
        db_table = "chatrooms"
        verbose_name = "Chat xona"
        verbose_name_plural = "Chat xonalari"
        constraints = [
            models.UniqueConstraint(
                fields=["chat_listing",'buyer'],
                name="unique_chat_listing_buyer",
            )
        ]

class Message(BaseModel):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="room_messages", db_index=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE,related_name="sender_messages", db_index=True)
    text = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Room id: {self.room.id} | Message from: {self.sender.username} | Message text: {self.text[:30]}"

    class Meta:
        db_table = "messages"
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"
        indexes = [
            models.Index(fields=["created_at"],name="message_created_at_idx")
        ]