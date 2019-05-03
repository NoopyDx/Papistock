from django.urls import path
from . import views

urlpatterns = [
    path('',views.accueil, name='accueil'),
    #path('index', views.index, name='index'),
    #path('genpdf', views.pdf, name='pdf'),
    #path('thx', views.land, name = 'land'),
    path('<parfum_text>/<number>/test', views.test, name='test'),
    path('<bac>/test', views.delete_stock, name='delete_stock'),
    path('accueil', views.accueil, name='accueil'),
    path('stocks', views.stocks, name='stocks'),
    path('commandes', views.commandes, name='commandes'),
    path('fabrication', views.fabrication, name='fabrication'),
    path('etiquettes', views.etiquettes, name='etiquettes'),
    path('<bac>/commandes', views.delete_order, name='delete_order'),
]
