import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from users.managers import CustomUserManager

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator

from django.dispatch import receiver
from django.db.models.signals import post_save


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')
    limit = 100 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 10 MiB.')



class User(AbstractBaseUser, PermissionsMixin):
    email=models.EmailField(max_length=50, unique=True)
    password=models.CharField(max_length=1000,validators=[MinLengthValidator(6)])
    father_name=models.CharField(max_length=50)
    first_name=models.CharField(max_length=50, null=True, blank=True)
    last_name=models.CharField(max_length=50, null=True, blank=True)
    born_date=models.DateField(null=True)
    is_translator = models.BooleanField(default=False)
    is_lawyer = models.BooleanField(default=False)
    is_client = models.BooleanField(default=True)
    about = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to="image/", null=True, blank=True, validators=[validate_file_extension])
    languages = models.CharField(max_length=250, null=True, blank=True)
    total_orders = models.IntegerField(null=True, blank=True, default=0)
    rating = models.FloatField(null=True, blank=True, default=0)
    comment = models.CharField(max_length=255, null=True, blank=True)
    cost = models.CharField(max_length=100, null=True, blank=True)
    pasport = models.FileField(upload_to='pasports/', validators=[validate_file_extension], null=True, blank=True)
    diplom = models.FileField(upload_to='diploms/', validators=[validate_file_extension], null=True, blank=True)
    diplom_text = models.TextField(null=True, blank=True)
    sertificate = models.FileField(upload_to='sertificate/', validators=[validate_file_extension], null=True, blank=True)
    sertificate_name = models.CharField(max_length=255, blank=True, null=True)

    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email



class Translator(models.Model):
    user=models.OneToOneField(User, related_name='translator', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.user.email

class Lawyer(models.Model):
    user=models.OneToOneField(User, related_name='lawyer', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.user.email 


class LawyerOrders(models.Model):
    file_lawyer=models.FileField(upload_to='order/lawyer/',  validators=[validate_file_extension])
    file_client=models.FileField(upload_to='order/lawyer/client/', validators=[validate_file_extension])
    lawyer = models.ForeignKey(User, related_name='lawyer_order', on_delete=models.CASCADE, null=True, blank=True)
    client = models.ForeignKey(User, related_name='client_u', on_delete=models.CASCADE, null=True, blank=True)
    ordered_date = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(upload_to='order/lawyer/image/', null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Result_Work ID: {self.id} | Lawyer: {self.lawyer} | Client: {self.client} | OrderedTime: {self.ordered_date}"
  


class TranslatorOrders(models.Model):
    client=models.ForeignKey(User, related_name='client', on_delete=models.CASCADE, null=True, blank=True)
    translator = models.ForeignKey(User, related_name='translator_order', on_delete=models.CASCADE, null=True, blank=True)
    file_trans=models.FileField(upload_to='order/trans/',  validators=[validate_file_extension], null=True, blank=True)
    client_file=models.FileField(upload_to='order/trans/client/', validators=[validate_file_extension], null=True, blank=True)
    order_id=models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='order/trans/image/', null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    file_trans_size=models.IntegerField(default=0, blank=True)
    ordered_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def clean(self):
    #     print('CLEANED_DATA')
    #     self.file_trans_size = self.file_trans.size

    


    def __str__(self):
        return f"Result_Work ID: {self.id} | Translator: {self.translator} | Client: {self.client} | OrderedTime: {self.ordered_time}"


    class Meta:
        verbose_name = "Translator's Work"
        verbose_name_plural = "Translator's Works"
        ordering = ['id']


    # @receiver(signal=post_save, sender=self.TranslatorOrders())
    # def attach_notification_to_client(sender, **kwargs):
    # file_trans = kwargs['instance']
    # if file_trans.file_trans is not None:
    #             trans = TranslatorOrders.objects.get()




class OrderCilent(models.Model):
    prose='prose'
    foself='frs'
    uzb = 'uzb'
    rus = 'rus'
    eng = 'eng'
    lawyer='lawyer'
    outlawyer='outlawyer'
    CHOISE1=[
        (prose,'prose'),
        (foself,'frs'),
    ]
    CHOISE2=[
        (uzb , 'uzb'),
        (rus , 'rus'),
        (eng , 'eng'),
    ]
    CHOISE3=[
        (uzb , 'uzb'),
        (rus , 'rus'),
        (eng , 'eng'),
    ]
    CHOISE4=[
        (1, 1),
        (2 , 2),
        (3 , 3),
        (4 , 4),
        (5 , 5),
    ]
    CHOISE5=[
        (lawyer , 'lawyer'),
        (outlawyer , 'outlawyer'),
    ]
    type_w = models.CharField(
        max_length=10,
        choices=CHOISE5,
        default='lawyer',
    )
    type_t = models.CharField(
        max_length=10,
        choices=CHOISE1,
        default='prose',
    )
    from_l=models.CharField(
        max_length=10,
        choices=CHOISE2,
        default='uzb',
    )
    to_l = models.CharField(
        max_length=10,
        choices=CHOISE3,
        default='eng',
    )
    

    file_order=models.FileField(upload_to='order/user/',  validators=[validate_file_extension])
    result_work=models.FileField(upload_to='order/user/trans/', null=True, validators=[validate_file_extension])
    result_work1=models.FileField(upload_to='order/user/result/', null=True, validators=[validate_file_extension])
    translator=models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='translator_work')
    lawyer=models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lawyer_work')
    client=models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='client_user')
    pages=models.IntegerField(null=True, blank=True)
    image_lawyer=models.FileField(upload_to='order/user/lawyer/',  validators=[validate_file_extension], null=True, blank=True)
    image_trans=models.FileField(upload_to='order/user/trans/',  validators=[validate_file_extension], null=True, blank=True)
    commit = models.TextField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    lawyer_time = models.DateTimeField(null=True, blank=True)
    trans_time = models.DateTimeField(null=True, blank=True)
    rate=models.IntegerField(default=0, null=True, blank=True, choices=CHOISE4)
    comment = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Order ID:{self.id} | Client: {self.client} | Translator: {self.translator}"

    class Meta:
        verbose_name = "Client's Order"
        verbose_name_plural = "Client's Orders"
        ordering = ['-id']


class Home(models.Model):
    Transcript = 'Transcript'
    Rec_letter = 'Rec_letter'
    uzb = 'uzb'
    rus = 'rus'
    eng = 'eng'
    CHOISE1 = [
        (Transcript, 'Transcript'),
        (Rec_letter, 'Rec_letter'),
    ]
    CHOISE2 = [
        (uzb, 'uzb'),
        (rus, 'rus'),
        (eng, 'eng'),
    ]
    CHOISE3 = [
        (uzb, 'uzb'),
        (rus, 'rus'),
        (eng, 'eng'),
    ]
    bir = '25$'
    ikki = '36$'
    uch = '45$'
    CHOISE = [
        (bir, 'bir'),
        (ikki, 'ikki'),
        (uch, 'uch'),
    ]
    definition = models.CharField(
        max_length=10,
        choices=CHOISE,
        default='bir',
        null=True,
    )
    type_doc = models.CharField(
        max_length=10,
        choices=CHOISE1,
        default='Transcript',
    )
    from_l = models.CharField(
        max_length=10,
        choices=CHOISE2,
        default='uzb',
    )
    to_l = models.CharField(
        max_length=10,
        choices=CHOISE3,
        default='eng',
    )
    com_a_sayt = models.TextField(null=True, blank=True)
    first_name=models.CharField(max_length=255, blank=True)
    com_date=models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
    


     


@receiver(signal=post_save, sender=OrderCilent)
def attach_notification_to_translator(sender, **kwargs):
   order = kwargs['instance']
   if order.file_order is not None:
            ClientNotification.objects.create(user=order.translator, client_order=order)
            
            
class ClientNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_n', null=True, blank=True)
    client_order = models.ForeignKey(OrderCilent, on_delete=models.CASCADE, related_name='client_notify', null=True, blank=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"(User_Notification ID : {self.id}) | Is_Read:{self.is_read} | For {self.user}"

    class Meta:
        ordering = ['id']
        verbose_name = 'Client Notification'
        verbose_name_plural = 'Client Notifications'

@receiver(signal=post_save, sender=TranslatorOrders)
def attach_notification_to_client(sender, **kwargs):
   file_trans = kwargs['instance']
   if file_trans.file_trans is not None:
            TranslatorNotification.objects.create(user=file_trans.client, trans_order=file_trans)   

class TranslatorNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='translator_n', null=True, blank=True)
    trans_order = models.ForeignKey(TranslatorOrders, on_delete=models.CASCADE, related_name='trans_notify', null=True, blank=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"(User_Notification ID : {self.id}) | Is_Read:{self.is_read} | For {self.user}"

    class Meta:
        ordering = ['id']
        verbose_name = 'Translator Notification'
        verbose_name_plural = 'Translator Notifications'


