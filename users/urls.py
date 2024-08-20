from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (ClientNotificationList, ClientMarkingAsReadNotificationDetail, ClientMarkingAsReadNotificationList,  UserRegisterView,LogoutUserView, LawyerDetailView, TranslatorDetailView, UserDetailView, LawyerListView,
TranslatorListView, ChangePasswordTranslatorView, ChangePasswordLawyerView, ChangePasswordClientView, RequestPasswordResetEmailClientView, PasswordTokenCheckAPIClientView, SetNewPasswordAPIClientView, OrderTranslator,
OrderLawyer,HomeView, ClientOrdersView, HomeTranslatorView,  OrderCilentDetailView, OrderTranslatorGetView, OrderClientGet, TranslatorMarkingAsReadNotificationDetail, TranslatorMarkingAsReadNotificationList,  TranslatorNotificationList,
                 OrderLawyerGetView   )


router=DefaultRouter()
router.register('translators', HomeTranslatorView, basename='translators')


urlpatterns=[
    path('page/', include(router.urls)),
    path('user/register/', UserRegisterView.as_view()),
    path('trans/register/', UserRegisterView.as_view()),
    path('lawyer/register/', UserRegisterView.as_view()),
    path('user/logout/', LogoutUserView.as_view()),
    path('trans/logout/', LogoutUserView.as_view()),
    path('lawyer/logout/', LogoutUserView.as_view()),
    path('user/user-detail/<int:pk>/', UserDetailView.as_view()),
    path('trans/user-detail/<int:pk>/', TranslatorDetailView.as_view()),
    path('lawyer/user-detail/<int:pk>/', LawyerDetailView.as_view()),
    path('lawyer/def/home', LawyerListView.as_view()),
    path('trans/def/home', TranslatorListView.as_view()),
    path('user/change_password/<int:pk>/', ChangePasswordClientView.as_view()),
    path('request-reset-email/', RequestPasswordResetEmailClientView.as_view(), name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPIClientView.as_view(), name='password-reset-confirm'),
    path('password-reset-complete', SetNewPasswordAPIClientView.as_view(), name='password-reset-complete'),
    path('trans/change_password/<int:pk>/', ChangePasswordTranslatorView.as_view()),
    path('lawyer/change_password/<int:pk>/', ChangePasswordLawyerView.as_view()),
    path('Home/', HomeView.as_view()),
    path('user/order/', ClientOrdersView.as_view()), # bu
    path('user/order/detail/<int:pk>/', OrderCilentDetailView.as_view()),
    path('trans/order/<int:pk>/', OrderTranslator.as_view()),
    path('user/order/get/', OrderClientGet.as_view()),  # bu
    path('trans/order/', OrderTranslatorGetView.as_view()),
    path('lawyer/order/', OrderLawyerGetView.as_view()),
    path('lawyer/order/<int:pk>/', OrderLawyer.as_view()),

    # notifications
    path('user/client/notification/', ClientNotificationList.as_view()),
    path('tanslator/notification/', TranslatorNotificationList.as_view()),
    path('user/client/notification/<int:pk>/', ClientMarkingAsReadNotificationDetail.as_view()),
    path('tanslator/notification/mark-as-read/', TranslatorMarkingAsReadNotificationList.as_view()),
    # path('user/client/notification/mark-as-read/<int:pk>/', ClientNotificationDetail.as_view()),
    # path('tanslator/notification/<int:pk>/', TranslatorNotificationDetail.as_view()),
    path('user/client/notification/mark-as-read/', ClientMarkingAsReadNotificationList.as_view()),
    path('tanslator/notification/mark-as-read/<int:pk>/', TranslatorMarkingAsReadNotificationDetail.as_view()),

]