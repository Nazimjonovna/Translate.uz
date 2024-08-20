from rest_framework import serializers
from users.models import User
from .models import Group, Message


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('id', 'name', 'translator', 'client')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id','sender', 'group', 'text')
    

    # def validate(self, data):
        
    #     if not data['sender']:
    #         raise serializers.ValidationError(f"'sender' field is required")
    #     if not data['group']:
    #         raise serializers.ValidationError(f"'group' field is required")
    #     if not data['text']:
    #         raise serializers.ValidationError(f"'text' field is required")

    #     return data