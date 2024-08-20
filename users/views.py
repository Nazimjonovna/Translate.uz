import os
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from rest_framework import parsers, status,  generics
from rest_framework.views import APIView
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import smart_str,  smart_bytes, DjangoUnicodeDecodeError
from django.urls import reverse
from django.http import Http404, HttpResponsePermanentRedirect
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.decorators import method_decorator
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from .utils import Util
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .serializers import  GetAccountTranslatorSerializer, GetOrdersClientSerializer, TranslatorNotificationSerializer, TranslatorOrdersSerializerGet,\
        UserRegisterSerializer,AccountTranslatorSerializer, AccountLawyerSerializer, AccountClientSerializer,\
        ChangePasswordTranslatorSerializer, ChangePasswordLawyerSerializer, ChangePasswordClientSerializer,\
        ResetPasswordEmailRequestClientSerializer, SetNewPasswordClientSerializer, TranslatorOrdersSerializer, LawyerOrdersSerializer,\
        HomeViewSerializers, OrdersClientSerializer, OrderCilentDetailSerializer, ClientNotificationSerializer, LawyerOrdersSerializerGet
   
from .models import Lawyer, Translator, User, Home, OrderCilent, TranslatorOrders, LawyerOrders, ClientNotification, TranslatorNotification
from chat.models import Group
from django.db.models import Avg

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView



class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']
sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2'
    )
)

# Create your views here.
class Transpaginations(PageNumberPagination):
    page_size=12

class HomeTranslatorView(viewsets.ModelViewSet):
    serializer_class=GetAccountTranslatorSerializer
    queryset=User.objects.filter(is_translator=True)
    pagination_class=Transpaginations

    def get(self, request, *args, **kwargs):
        serializer=GetAccountTranslatorSerializer(User.objects.all(), many=True)

        return Response(serializer.data,  status=status.HTTP_200_OK)

#REGISTRATSIYA VIEW_____________

class UserRegisterView(generics.GenericAPIView):
    parser_classes = [parsers.MultiPartParser , parsers.FileUploadParser, ]
    serializer_class=UserRegisterSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserRegisterSerializer)
    def post(self, request, *args, **kwargs):
        request.POST._mutable = True
        password = request.data['password'][:]
        request.data['password'] = make_password(password)
        serializer = True
        request.POST._mutable = False

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            email = serializer.data['email']
            user = User.objects.get(email=email)
            access_token = AccessToken().for_user(user)
            refresh_token = RefreshToken().for_user(user)

            if serializer.data['is_translator'] == True:
                Translator.objects.create(user=user)
            elif serializer.data['is_lawyer'] == True:
                Lawyer.objects.create(user=user)

            return Response({
                "access_token": str(access_token),
                "refresh_token": str(refresh_token),
                "user":serializer.data,
            })
        else:
            return Response(serializer.errors)


#LOG_OUT VIEW__________________________

class LogoutUserView(APIView):
    def post(self, request):
        response=Response()
        response.delete_cookie(key='refreshToken')
        response.data={
            'massage':'success'
        }
        return response


#LIST VIEW_______________________
        
class LawyerListView(generics.ListAPIView):
    # parser_classes = [parsers.MultiPartParser, ]
    queryset = User.objects.filter(is_lawyer=True)
    serializer_class= AccountLawyerSerializer

    # def get(self, request):
    #     lawyers = Lawyer.objects.all()
    #     serializer = LawyerSerializer(lawyers, many=True)
    #     return Response(serializer.data)

class TranslatorListView(generics.ListAPIView):
    queryset = User.objects.filter(is_translator=True)
    serializer_class= GetAccountTranslatorSerializer
    # parser_classes = [parsers.MultiPartParser, ]

    def get(self, request):
        translators = User.objects.filter(is_translator=True)
        serializer = GetAccountTranslatorSerializer(translators, many=True)
        return Response(serializer.data)              

#UPDATE VIEW_______________________

class LawyerDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, ]
    parser_classes = [parsers.MultiPartParser]
    queryset=User.objects.all()
    serializer_class=AccountLawyerSerializer

    def get(self, request, pk):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = AccountLawyerSerializer(user)
            return Response(serializer.data)

    @swagger_auto_schema(request_body=AccountLawyerSerializer)
    def patch(self, request, pk):
        user = User.objects.get(id=pk)
        user.cost=request.data.get('cost', user.cost)
        user.about=request.data.get('about', user.about)
        if user.email!=request.data['email']:
            user.email=request.data.get('email', user.email)
            us = User.objects.filter(email=request.data['email'])
            if not us.exists():
                    user.save()
                    access_token = AccessToken().for_user(user)
                    refresh_token = RefreshToken().for_user(user)
                    serializer =AccountLawyerSerializer(instance=user, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({
                            "access_token": str(access_token),
                            "refresh_token": str(refresh_token),
                            "user":serializer.data,
                            })
                    else:
                        return Response({'User not found'},
                                        serializer.errors)
            else:
                    return Response({"Mavjud email"}, status=status.HTTP_400_BAD_REQUEST)  
        else:
            user.save()
            serializer =AccountClientSerializer(instance=user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "user":serializer.data,
                    })
            else:
                return Response({'User not found'},
                                serializer.errors)

    def delete(self, request, pk):
        user = User.objects.get(id=pk)

        if user:
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TranslatorDetailView(APIView):  
    permission_classes = [IsAuthenticated, ]
    parser_classes = [parsers.MultiPartParser]
    serializer_class=AccountTranslatorSerializer

    def get(self, request, pk):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = GetAccountTranslatorSerializer(user)
            return Response(serializer.data)

    @swagger_auto_schema(request_body=AccountTranslatorSerializer)
    def patch(self, request, pk):
        user = User.objects.get(id=pk)
        user.cost=request.data.get('cost', user.cost)
        user.about=request.data.get('about', user.about)
        
        if user.email!=request.data['email']:
            user.email=request.data.get('email', user.email)
            us = User.objects.filter(email=request.data['email'])
            if not us.exists():
                    user.save()
                    access_token = AccessToken().for_user(user)
                    refresh_token = RefreshToken().for_user(user)
                    serializer =AccountTranslatorSerializer(instance=user, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        user.languages = serializer.data.get('language_choice', user.languages)
                        user.diplom_text = serializer.data.get('diplom_text', user.diplom_text)
                        user.sertificate_name = serializer.data.get('sertificate_name', user.sertificate_name)
                        user.save()
                        return Response({
                            "access_token": str(access_token),
                            "refresh_token": str(refresh_token),
                            "user":serializer.data,
                            })
                    else:
                        return Response({'User not found'},
                                        serializer.errors)
            else:
                    return Response({"Mavjud email"}, status=status.HTTP_400_BAD_REQUEST)  
        else:
            user.save()
            serializer =AccountTranslatorSerializer(instance=user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                user.languages = serializer.data.get('language_choice', user.languages)
                user.diplom_text = serializer.data.get('diplom_text', user.diplom_text)
                user.sertificate_name = serializer.data.get('sertificate_name', user.sertificate_name)
                user.save()
                return Response({
                    "user":serializer.data,
                    })
            else:
                return Response({'User not found'},
                                serializer.errors)

    def delete(self, request, pk):
        user = User.objects.get(id=pk)

        if user:
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated, ]
    parser_classes = [parsers.MultiPartParser,]

    def get(self, request, pk):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = AccountClientSerializer(user)
            return Response(serializer.data)

    @swagger_auto_schema(request_body=AccountClientSerializer)
    def patch(self, request, pk):
        user = User.objects.get(id=pk)
        if user.email!=request.data['email']:
            us = User.objects.filter(email=request.data['email'])
            if not us.exists():
                user.email=request.data.get('email', user.email)
                user.save()
                access_token = AccessToken().for_user(user)
                refresh_token = RefreshToken().for_user(user)
                serializer =AccountClientSerializer(instance=user, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        "access_token": str(access_token),
                        "refresh_token": str(refresh_token),
                        "user":serializer.data,
                        })
                else:
                    return Response({'User not found'},
                                    serializer.errors)
            else:
                return Response({"Mavjud email"}, status=status.HTTP_400_BAD_REQUEST)  
        else:
            user.save()
            serializer =AccountClientSerializer(instance=user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "user":serializer.data,
                    })
            else:
                return Response({'User not found'},
                                serializer.errors)


    def delete(self, request, pk):
        user = User.objects.get(id=pk)

        if user:
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)          


class ChangePasswordTranslatorView(generics.UpdateAPIView):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordTranslatorSerializer

    @swagger_auto_schema(request_body=ChangePasswordTranslatorSerializer)
    def patch(self, request, *args, **kwargs):
        serializer = ChangePasswordTranslatorSerializer(instance=self.request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': 'Password successfully updated'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors)


class OrderTranslator(APIView):
    serializer_class = TranslatorOrdersSerializer
    parser_classes = [parsers.MultiPartParser]
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(request_body=TranslatorOrdersSerializer)    
    def patch(self, request, pk):
        order = TranslatorOrders.objects.get(id=pk)
        serializer = TranslatorOrdersSerializer(instance=order, data=request.data, partial=True) 
        # serializer = TranslatorOrdersSerializer(data=request.data, partial=True) 
        serializer.is_valid(raise_exception=True)
        serializer.save()
        order.file_trans_size=order.file_trans.size
        order.save()
        c_order = OrderCilent.objects.get(id=order.order_id)
        c_order.result_work=request.FILES['file_trans']
        c_order.save()
        return Response(serializer.data)
        


class OrderTranslatorGetView(generics.ListAPIView):
    serializer_class = TranslatorOrdersSerializerGet
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FileUploadParser]
    queryset = TranslatorOrders.objects.all()

    def get_queryset(self):
        translator=User.objects.get(email=self.request.user, is_translator=True)
        return translator.translator_order.all()

    # def get(self, request, *args, **kwargs):
    #     seializer=TranslatorOrdersSerializerGet(User.objects.get(email=request.user.email, is_translator=True))



    

class ChangePasswordLawyerView(generics.UpdateAPIView):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordLawyerSerializer

    @swagger_auto_schema(request_body=ChangePasswordLawyerSerializer)
    def patch(self, request, *args, **kwargs):
        serializer = ChangePasswordLawyerSerializer(instance=self.request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': 'Password successfully updated'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors)
 

class ChangePasswordClientView(generics.UpdateAPIView):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordClientSerializer
    
    @swagger_auto_schema(request_body=ChangePasswordClientSerializer)
    def patch(self, request, *args, **kwargs):
        serializer = ChangePasswordClientSerializer(instance=self.request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg': 'Password successfully updated'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors)


class RequestPasswordResetEmailClientView(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestClientSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(
                request=request).domain
            relativeLink = reverse(
                'password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://' + current_site + relativeLink
            email_body = 'Hello, \n Use link below to reset your password  \n' + \
                         absurl + "?redirect_url=" + redirect_url
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Reset your passsword'}
            Util.send_email(data)
            return Response({'success': 'We have sent you a link to reset your password', "link":relativeLink, "uidb64":uidb64, 'token':token,}, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'Requested email was not found' }, status=status.HTTP_404_NOT_FOUND)


class PasswordTokenCheckAPIClientView(generics.GenericAPIView):
    serializer_class = SetNewPasswordClientSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url + '?token_valid=False')
                else:
                    return CustomRedirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(
                    redirect_url + '?token_valid=True&message=Credentials Valid&uidb64=' + uidb64 + '&token=' + token)
            else:
                return CustomRedirect(os.environ.get('FRONTEND_URL', '') + '?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url + '?token_valid=False')

            except UnboundLocalError as e:
                return Response({'error': 'Token is not valid, please request a new one'},
                                status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIClientView(generics.GenericAPIView):
    serializer_class = SetNewPasswordClientSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)



class HomeView(APIView):
    queryset=User.objects.all()
    serializer_class=HomeViewSerializers
    def get(self, request, *args, **kwargs):
        serializer=HomeViewSerializers(Home.objects.all(), many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=HomeViewSerializers)
    def post(self, request):
        serializer=HomeViewSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(request.data)



class ClientOrdersView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, ]
    parser_classes = [parsers.MultiPartParser, parsers.FileUploadParser]
    serializer_class = OrdersClientSerializer
    # queryset = OrderCilent.objects.all()                

    @swagger_auto_schema(request_body=OrdersClientSerializer)
    def post(self, request):
        serializer = OrdersClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
           
            if serializer.data['type_w']=='lawyer':
                translator_id=serializer.data['translator']
                user=User.objects.get(email=request.user)
                translator = User.objects.get(id=translator_id)
                order_crtd=TranslatorOrders.objects.create(client=user, translator=translator, ordered_time=serializer.data['created_at'], image=user.image,  first_name=user.first_name, client_file=request.FILES['file_order'], order_id=serializer.data['id'])

                lawyers=User.objects.filter(is_lawyer=True)
                for lawyer in lawyers:  #endi qo'shildi
                    buyurmas=LawyerOrders.objects.filter(lawyer=lawyer.id)
                    if  buyurmas:
                        for buyutma in buyurmas:
                            if buyutma.file_client:
                                if  buyutma.file_lawyer:
                                    usel=User.objects.get(email=request.user, is_client=True)
                                    ordel=LawyerOrders()
                                    lawyer_id=lawyer.id
                                    continue     
                    else:      
                         usel=User.objects.get(email=request.user, is_client=True)  
                         ordel=LawyerOrders()
                         lawyer_id=lawyer.id  


                
                lawyer = User.objects.get(id=lawyer_id)
                ordel.client = usel
                ordel.lawyer = lawyer
                ordel.ordered_date = serializer.data['created_at']
                ordel.file_client = serializer.data['file_order']
                ordel.image = usel.image
                ordel.first_name = usel.first_name
                ordel.save()
                Group.objects.create(client=user, translator=translator, lawyer=lawyer)
                return Response(serializer.data)

            else:
                try:
                    translator_id=serializer.data['translator']
                   
                    user=User.objects.get(email=request.user)
                    translator = User.objects.get(id=translator_id)
                    order_crtd=TranslatorOrders.objects.create(client=user, translator=translator, ordered_time=serializer.data['created_at'], image=user.image,  first_name=user.first_name, order_id=serializer.data['id'])
                    Group.objects.create(client=user, translator=translator)
                    return Response(serializer.data)
                    
                finally:
                     order_crtd.client_file=request.FILES['file_order']
                     order_crtd.save()
        else:
            return Response(serializer.errors)        

                
            
class OrderClientGet(generics.ListAPIView):
    serializer_class = GetOrdersClientSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FileUploadParser]
    queryset = OrderCilent.objects.all()

    def get_queryset(self):
        user=User.objects.get(email=self.request.user, is_client=True)
        order_u=OrderCilent.objects.filter(client=user.id)
        for o_u in order_u:
            translator = User.objects.get(id=o_u.translator.id)
            o_u.image_trans = translator.image
            o_u.trans_time = translator.created_at
            if o_u.lawyer:
                lawyer=User.objects.get(id=o_u.lawyer)
                o_u.image_lawyer = lawyer.image
                o_u.lawyer_time = lawyer.created_at
                o_u.save()
            o_u.save()
        return user.client_user.all()


class OrderLawyer(APIView):
    serializer_class = LawyerOrdersSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FileUploadParser]
    permission_classes = [IsAuthenticated, ]

    @swagger_auto_schema(request_body=LawyerOrdersSerializer)    
    def patch(self, request, pk):
        l_order = LawyerOrders.objects.get(id=pk)
        serializer = LawyerOrdersSerializer(instance=l_order, data=request.data, partial=True) 
        l_order.file_lawyer=request.data['file_lawyer']
        l_order.save()
        
        c_order = OrderCilent.objects.get(created_at=l_order.ordered_date)
        c_order.result_work1=request.data['file_lawyer']
        c_order.save()

        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return Response(serializer.data)
        return Response(serializer.errors)


class OrderLawyerGetView(generics.ListAPIView):
    serializer_class = LawyerOrdersSerializerGet
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FileUploadParser]
    queryset = LawyerOrders.objects.all()

    def get_queryset(self):
        lawyer=User.objects.get(email=self.request.user, is_lawyer=True)
        return lawyer.lawyer_order.all()


class OrderCilentDetailView(APIView):
    permission_classes = [IsAuthenticated,]

    @swagger_auto_schema(request_body=OrderCilentDetailSerializer)
    def patch(self, request, pk):
        order = OrderCilent.objects.get(id=pk)
        serializer=OrderCilentDetailSerializer(instance=order, data=request.data, partial=True)
        order.rate=request.data.get('rate', order.rate)
        order.comment=request.data.get('comment', order.comment)
        order.save()
        if serializer.is_valid():
            serializer.save()
            translator=User.objects.get(is_translator=True, email=order.translator)
            rating = OrderCilent.objects.filter(translator=translator).aggregate(Avg('rate'))
            total_orders = OrderCilent.objects.filter(translator=translator).count()
            translator.rating=round(rating['rate__avg'], 1) 
            translator.total_orders = total_orders
            translator.comment = order.comment
            translator.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors,)


class ClientNotificationList(generics.ListAPIView):
    serializer_class = TranslatorNotificationSerializer
    queryset = ClientNotification.objects.filter(is_read=False)
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['user'])
    def get(self, request):
        if request.user.is_client == True:
            user_notifs = request.user.client_n.filter(is_read=False)
            serializer = self.serializer_class(user_notifs, many=True)
            return Response(serializer.data)
        else:
            return Response("You are not allowed to read")


class TranslatorNotificationList(generics.ListAPIView):
    serializer_class = ClientNotificationSerializer
    queryset = TranslatorNotification.objects.filter(is_read=False)
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_translator == True:
            user_notifs = request.user.translator_n.filter(is_read=False)
            serializer = self.serializer_class(user_notifs, many=True)
            return Response(serializer.data)
        else:
            return Response("You are not allowed to read")



class ClientMarkingAsReadNotificationList(generics.ListAPIView):
    serializer_class = TranslatorNotificationSerializer
    queryset = ClientNotification.objects.filter(is_read=False)
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(tags=['user'])
    def get(self, request):
        if request.user.is_client == True:
            notifications = ClientNotification.objects.filter(user=request.user.id, is_read=False)
            if len(notifications) > 0:
                notifications.update(is_read=True)
                return Response({'message': 'All message successfully read!'})
            else:
                return Response({'message': 'All message has been already read!'})
        else:
            return Response("You are not allowed to read")


class ClientMarkingAsReadNotificationDetail(generics.RetrieveAPIView): 
    serializer_class = TranslatorNotificationSerializer
    queryset = ClientNotification.objects.filter(is_read=False)
    permission_classes = [IsAuthenticated]
    my_tags = ['user']

    @swagger_auto_schema(tags=['user'])
    def get(self, request, pk):
        try:
            if request.user.is_client == True:
                notif = ClientNotification.objects.get(id=pk)
                notif.is_read=True
                notif.save()
                return Response({'msg': 'This message successfully read!'})
            return Response("You are not allowed to read")    
        except :
            return Response("You to read")
            


    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()


class TranslatorMarkingAsReadNotificationList(generics.ListAPIView):
    serializer_class = ClientNotificationSerializer
    queryset = TranslatorNotification.objects.filter(is_read=False)
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(tags=['user'])
    def get(self, request):
        if request.user.is_translator == True:
            notifications = TranslatorNotification.objects.filter(user=request.user.id, is_read=False)
            if len(notifications) > 0:
                notifications.update(is_read=True)
                return Response({'message': 'All message successfully read!'})
            else:
                return Response({'message': 'All message has been already read!'})
        else:
            return Response("You are not allowed to read")



class TranslatorMarkingAsReadNotificationDetail(generics.RetrieveAPIView):
    serializer_class = ClientNotificationSerializer
    queryset = TranslatorNotification.objects.filter(is_read=False)
    permission_classes = [IsAuthenticated]
    my_tags = ['user']

    @swagger_auto_schema(tags=['user'])
    def get(self, request, pk):
        try:
            if request.user.is_translator == True:
                notif = TranslatorNotification.objects.get(id=pk)
                notif.is_read=True
                notif.save()
                return Response({'msg': 'This message successfully read!'})
        except:
            return Response("You are not allowed to read")

    def get_parsers(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_parsers()        
        