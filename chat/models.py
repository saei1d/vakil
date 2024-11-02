from django.db import models

from users.models import Client


class ChatMessageVakil(models.Model):
    sender = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
