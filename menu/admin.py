from django.contrib import admin
from .models import Kategoriya, Taom, Buyurtma


@admin.register(Kategoriya)
class KategoriyaAdmin(admin.ModelAdmin):
    list_display = ['emoji', 'nom']


@admin.register(Taom)
class TaomAdmin(admin.ModelAdmin):
    list_display = ['nom', 'kategoriya', 'narx', 'mavjud']
    list_filter = ['kategoriya', 'mavjud']
    list_editable = ['narx', 'mavjud']
    search_fields = ['nom']


@admin.register(Buyurtma)
class BuyurtmaAdmin(admin.ModelAdmin):
    list_display = ['id', 'mijoz', 'telefon', 'taom', 'miqdor', 'jami_narx_formatted', 'status', 'vaqt']
    list_filter = ['status', 'vaqt']
    list_editable = ['status']
    search_fields = ['mijoz', 'telefon']
    readonly_fields = ['vaqt', 'foydalanuvchi']
