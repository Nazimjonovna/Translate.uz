from pprint import pprint
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from .models import User, OrderCilent, Home, LawyerOrders, TranslatorOrders, ClientNotification, TranslatorNotification



class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())])
    class Meta:
        model=User
        fields=['id', 'first_name', 'last_name', 'father_name', 'email', 'password', 'image', 'pasport', 'sertificate', 'diplom', 'is_lawyer', 'is_translator',
                "is_client", 'born_date']  


class AccountTranslatorSerializer(serializers.ModelSerializer):
    CHOICE = (
        ('english', 'English'),
        ('french', 'French'),
        ('russian', 'Russian'),
    )

    language_choice = serializers.MultipleChoiceField(
                        choices = CHOICE)
    class Meta:
        model=User
        fields= ['id', 'first_name', 'last_name', 'father_name', 'password', 'image', 'cost', 'about', 'born_date', 'email', 'diplom_text', 'sertificate_name', 'rating', 'total_orders', 'language_choice']
        read_only_fields = ['password',]

    def to_representation(self, instance):
        return super().to_representation(instance)

import os.path

def convert_bytes(size):
    """ Convert bytes to KB, or MB or GB"""
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0

FULL_PATH = '/home/norbek/proje/translateuz-backend/'
FULL_PATH_ON_SERVER = '/opt/translateuz-backend/'

class GetAccountTranslatorSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields= ['id', 'first_name', 'last_name', 'father_name', 'password', 'image', 'cost', 'about', 'born_date', 'email', 'languages', 'rating', 'comment', 'diplom', 'sertificate', 'total_orders']
        read_only_fields = ['password',]

    def to_representation(self, instance):
        try:
            data = super().to_representation(instance)
            if data['languages']:
                for i in data:
                    if i == 'languages':
                        data[i] = list(eval(data[i]))
                return data
            else:
                data['languages'] = []
                return data
        except:
            data['languages'] = []
            return data
            # raise ValueError('Invalid representation')



    

class ChangePasswordTranslatorSerializer(serializers.ModelSerializer):
    old_password=serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'password2']

    def validate(self, attrs):
        if attrs['new_password'] != attrs['password2']:
            raise serializers.ValidationError({'passwords': "The two password fields didn't match."})
        return super().validate(attrs)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['old_password']):
            raise serializers.ValidationError({'old_password': 'wrong password'})
        instance.password = validated_data.get('password', instance.password)

        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class TranslatorOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model=TranslatorOrders
        fields= ('file_trans',)
        read_only_fields = ['client', 'translator', 'cost', 'file_trans_size']


class TranslatorOrdersSerializerGet(serializers.ModelSerializer):
    class Meta:
        model=TranslatorOrders
        fields= '__all__'

        def to_representation(self, instance):
            file_trans = str(instance.file_trans)
            
            representation = super(TranslatorOrdersSerializerGet, self).to_representation(instance)
            representation['file_trans_sizeee'] = convert_bytes(os.path.getsize(FULL_PATH_ON_SERVER+'/media/'+file_trans))
            return representation

    

class AccountLawyerSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields= ['id',  'first_name', 'last_name', 'father_name', 'password', 'image', 'cost', 'about', 'born_date', 'email', 'diplom', 'sertificate']
        read_only_fields = ['password',]       

class ChangePasswordLawyerSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'password2']

    def validate(self, attrs):
        if attrs['new_password'] != attrs['password2']:
            raise serializers.ValidationError({'passwords': "The two password fields didn't match."})
        return super().validate(attrs)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['old_password']):
            raise serializers.ValidationError({'old_password': 'wrong password'})
        instance.password = validated_data.get('password', instance.password)

        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
 

class LawyerOrdersSerializerGet(serializers.ModelSerializer):
    class Meta:
        model=LawyerOrders
        fields='__all__'

class LawyerOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model=LawyerOrders
        fields= ['file_lawyer']
        read_only_fields = ['client', 'lawyer', 'cost']   

         

class AccountClientSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id',  'first_name', 'last_name', 'father_name', 'password', 'image', 'born_date', 'email']
        read_only_fields = ['password',]

class ChangePasswordClientSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True, write_only=True, min_length=6)
    new_password = serializers.CharField(required=True, write_only=True, min_length=6)
    password2 = serializers.CharField(required=True, write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'password2']

    def validate(self, attrs):
        if attrs['new_password'] != attrs['password2']:
            raise serializers.ValidationError({'passwords': "The two password fields didn't match."})
        return super().validate(attrs)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['old_password']):
            raise serializers.ValidationError({'old_password': 'wrong password'})
        instance.password = validated_data.get('password', instance.password)

        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

class ResetPasswordEmailRequestClientSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']

class SetNewPasswordClientSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)

class HomeViewSerializers(serializers.ModelSerializer):
    class Meta:
        model=Home
        fields="__all__"

class OrdersClientSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderCilent
        fields="__all__"
        

class GetOrdersClientSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderCilent
        fields= "__all__"    

    def to_representation(self, instance):
            representation = super(GetOrdersClientSerializer, self).to_representation(instance)
            representation['file_order_size'] = instance.file_order.size
            return representation         


class OrderCilentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=OrderCilent
        fields = ['rate', 'comment']
        

class TranslatorNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientNotification
        fields = (
            'id',
            )
    
    def to_representation(self, instance):
        representation = super(TranslatorNotificationSerializer, self).to_representation(instance)
        representation['title'] = "Yangi xabar"
        representation['text'] = f"Sizda {instance.trans_notify.client.email} tomonidan xabar bor!"
        # representation['ordered_file'] = instance.trans_order.file_trans
        # representation['created_at'] = instance.trans_order.created_at
        return representation


class ClientNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslatorNotification
        fields = (
            'id',
            )
    
    def to_representation(self, instance):
        representation = super(ClientNotificationSerializer, self).to_representation(instance)
        representation['title'] = "Yangi xabar"
        representation['text'] = f"Sizda {instance.client_notify.translator.email} tomonidan xabar bor!"
        # representation['ordered_file'] = instance.trans_notifications.file_trans
        # representation['created_at'] = instance.trans_notifications.created_at
        return representation



# from . import google
# from .register import register_social_user
import os
from rest_framework.exceptions import AuthenticationFailed


# class GoogleSocialAuthSerializer(serializers.Serializer):
#     auth_token = serializers.CharField()

#     def validate_auth_token(self, auth_token):
#         user_data = google.Google.validate(auth_token)
#         try:
#             user_data['sub']
#         except:
#             raise serializers.ValidationError(
#                 'The token is invalid or expired. Please login again.'
#             )

#         if user_data['aud'] != os.environ.get('GOOGLE_CLIENT_ID'):

#             raise AuthenticationFailed('oops, who are you?')

#         user_id = user_data['sub']
#         email = user_data['email']
#         provider = 'google'

#         return register_social_user(
#             provider=provider, user_id=user_id, email=email)       