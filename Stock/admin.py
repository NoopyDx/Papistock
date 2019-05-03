# Register your models here.
from django.contrib import admin

from .models import Glace, Parfum, Franchise

#Gestion des BDD Glace & Parfum dans le panel admin
class GlaceAdmin(admin.ModelAdmin):
    list_display = ('parfum_text', 'poids', 'date_prod', 'status', 'parfum_id', 'franchise_name', 'id')
    search_fields = ('status', 'parfum_text')
    list_per_page = 25

class ParfumAdmin(admin.ModelAdmin):
    list_display = ('parfum_text', 'sorbet')
    search_fields = ('parfum_text', 'sorbet')
    
admin.site.register(Glace, GlaceAdmin)
admin.site.register(Parfum, ParfumAdmin)
admin.site.register(Franchise)
