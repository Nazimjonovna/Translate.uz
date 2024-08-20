from django.shortcuts import get_object_or_404, render
from rest_framework import pagination, status, generics, parsers, permissions
from rest_framework.views import Response
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView

# from chat.serializers import Messgeserializer, Roomserializer
# from .models import RoomChat, RoomChatMessage
from users.models import User

# Create your views here.
class ChatPagination(pagination.PageNumberPagination):
    permission_classes = [permissions.IsAuthenticated]
    # page_size = 10
    # page_size_query_param = 'page_size'
    # max_page_size = 100

class RoomListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    # queryset = RoomChat.objects.all()
    # serializer_class = Roomserializer

    # def get(self, request, pk, *args, **kwargs):
    #     user=User.objects.get(id=pk)
    #     if user:
    #         RoomChat.objects.create()
    #     else:
    #         return Response({"user is not found"})    



class MessageView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    # queryset = RoomChatMessage.objects.all()
    # serializer_class = Messgeserializer
    # parser_classes = (parsers.MultiPartParser, parsers.FileUploadParser)

    # def post(self, request):
    #     serializer = self.serializer_class(data=request.data, context={'files': request.FILES, 'user': request.user})
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


def room(request, pk):
    # room:RoomChat=get_object_or_404(RoomChat, pk=pk)
    return room

class MessageCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    # serializer_class = Messgeserializer
    # queryset = RoomChatMessage.objects.all()
    parser_classes = (MultiPartParser, FileUploadParser)
    # my_tags = ['chat']

    # def post(self, request):
    #     serializer = self.serializer_class(data=request.data, context={'files': request.FILES, 'user': request.user})
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    # # def get_parsers(self):
    # #     if getattr(self, 'swagger_fake_view', False):
    # #         return []
    # #     return super().get_parsers()

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)

        





