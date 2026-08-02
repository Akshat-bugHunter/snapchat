from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.
class FriendRequest(models.Model):

    class StatusChoice(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"

    from_user = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE, related_name="sent_requests"
    )
    to_user = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE, related_name="received_requests"
    )

    status = models.CharField(
        max_length=10, choices=StatusChoice.choices, default=StatusChoice.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("from_user", "to_user")

    def __str__(self):
        return f"{self.from_user} -> {self.to_user}: {self.status}"


class Message(models.Model):
    sender = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE, related_name="recieved_messages"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.sender} -> {self.receiver}"
