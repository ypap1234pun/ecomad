from django.contrib import admin
from .models import shippingAddress,Order,OrderItem
from django.contrib.auth.models import User

admin.site.register(shippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)

# Create order Item Inline
class OrderItemInline(admin.StackedInline):
   model = OrderItem
   extra = 0

  #Extend our Order Model
class OrderAdmin(admin.ModelAdmin):
   model = Order
   readonly_fields = ["date_ordered"]
   fields =["user","full_name","email","shipping_address","amount_paid","date_ordered","shipped","date_shipped"]
   inlines = [OrderItemInline]

admin.site.unregister(Order)

admin.site.register(Order,OrderAdmin)