from django.contrib import admin
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db import models
from .models import Group, Message

# # Register your models here.
# class RoomChatAdmin(admin.ModelAdmin):
#     list_display=['id', 'room']
#     search_fields=['id', 'room']
#     list_display=['id', ]
#     class Meta:
#         model=RoomChat

# admin.site.register(RoomChat, RoomChatAdmin)
admin.site.register(Group)
admin.site.register(Message)

# class CachingPaginator(Paginator):
#     def _get_count(self):
#         if not hasattr(self, "_count"):
#             self._count=None
#             if self._count is None:
#                 try:
#                     key='adm:{0}:count'.format(hash(self.object_list.query.__str__()))
#                     self._count=cache.get(key, -1)
#                     if self._count == -1:
#                         self._count=super().count
#                         cache.set(key, self._count, 3600)

#                 except:
#                     self._count=len(self.object_list)

#             return self._count

#     count=property(_get_count)

# class RoomChatMessageAdmin(admin.ModelAdmin):
#     list_display=['room', 'reciever', 'sender', 'time', 'message']  
#     list_filter=['room', 'reciever', 'sender', 'time'] 
#     search_fields=['room__name', 'reciever__email', 'sender__email', 'message'] 
#     readonly_fields=['id', 'reciever', 'sender', 'time', 'room'] 

#     show_full_result_count=False
#     paginator=CachingPaginator

#     class Meta:
#         model=RoomChatMessage

# admin.site.register(RoomChatMessage, RoomChatMessageAdmin)
