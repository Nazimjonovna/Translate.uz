from django.contrib import admin
from .models import User, Translator, Lawyer, OrderCilent, TranslatorOrders, ClientNotification , TranslatorNotification, LawyerOrders
 
# Register your models here.
admin.site.register(User)
admin.site.register(Translator)
admin.site.register(Lawyer)
# admin.site.register(OrderCilent)
admin.site.register(LawyerOrders)
admin.site.register(ClientNotification)
admin.site.register(TranslatorNotification)

admin.site.register(TranslatorOrders)



@admin.register(OrderCilent)
class OrderCilentAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_order','image_trans', 'translator', 'trans_time', 'created_at')
    # list_editable = ('user', 'first_name', 'last_name', 'middle_name', 'birth_date', 'parent_phone_number')
    # search_fields = ('first_name', 'last_name', 'middle_name', 'birth_date', 'parent_phone_number')
    # ordering = ('first_name', 'last_name', 'middle_name', 'birth_date', 'parent_phone_number')
