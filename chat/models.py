from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    translator = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='gr_translator', null=True, blank=True)
    lawyer = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='gr_lawyer', null=True, blank=True)
    client = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='gr_client', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='gr_messages')
    text = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text