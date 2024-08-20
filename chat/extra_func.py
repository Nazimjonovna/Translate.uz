from chat.models import Group, Message
from chat.serializers import MessageSerializer, GroupSerializer
from asgiref.sync import sync_to_async


@sync_to_async
def get_chats_by_user(user):
    print(user)
    if user.is_client:
        chats = Group.objects.filter(client=user)
    elif user.is_translator:
        chats = Group.objects.filter(translator=user)
    elif user.is_lawyer:
        chats = Group.objects.filter(lawyer=user)

    serializer = GroupSerializer(chats, many=True)
    # return {'result': serializer.data}
    return serializer.data


@sync_to_async
def create_msg(content):
    serializer = MessageSerializer(data=content)
    print(serializer.is_valid())
    if serializer.is_valid():
        serializer.save()
        return serializer.data
    return serializer.errors