from channels.generic.websocket import AsyncJsonWebsocketConsumer 
from json.decoder import JSONDecodeError

from chat.extra_func import get_chats_by_user, create_msg
import json

from chat.models import Group, Message
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async


channel_layer = get_channel_layer()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):

        user = self.scope.get('user', False)
        await self.accept()

        if user.is_anonymous:
            await self.send_json({"user": str(user), 'errors': user.get_errors})
            return await self.close()
            
        return await self.send(
            json.dumps(
                        {
                            "message": "User connected", 
                            "user": str(user.id),
                            "groups": await get_chats_by_user(user)
                        }
                    )
                )

    async def receive(self, text_data):

        try:
            content = json.loads(text_data)
            if not isinstance(content, dict):
                return await self.send(
                                json.dumps(
                                    {
                                        'error': 'expected type json, got str instead'
                                    }
                                )
                            )
        except JSONDecodeError as e:
            return await self.send(json.dumps({'error': str(e)}))
        
        user = self.scope.get('user', False)
        ACTIONS = ['select-group']
        action = content.pop('action', False)
       
        response = {
            'action': action
        }

        if action == 'select-group':
            self.room_group_name = str(await self.get_group(content['group_id']))
            messages =  await self.get_messages(content['group_id'])
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            return await self.select_group({"data": {'Selected Group': self.room_group_name, "messages": messages}}) 


        elif action == 'send-message':
            group = str(await self.get_group(content['group_id']))
            content['sender'] = user.id
            content['group'] = group
            result = await create_msg(content)
            print('CONTENT_TYPE', content)
            return await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_message',
                    "text": result
                }
            )


    async def select_group(self, event):
        data = event['data']
        return await self.send_json(data)


    @database_sync_to_async
    def get_group(self, id):
        return Group.objects.get(id=id)

    
    @database_sync_to_async
    def get_messages(self, id):
        msgs = Message.objects.filter(group=id)
        dic = {}
        for msg in msgs:
            dic[msg.id] = msg.text
        return  dic

    async def send_message(self, event):
        data = event['text']
        await self.send_json(data)


    async def disconnect(self, code):
        user = self.scope.get('user', False)
        try:
            if not user.is_anonymous:
                await self.channel_layer.group_discard(
                            self.room_group_name,
                            self.channel_name
                        )
        except:
            pass
        finally:
            return await super().disconnect(code)
            