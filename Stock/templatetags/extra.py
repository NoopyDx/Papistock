from django import template
from ..models import Glace
register = template.Library()

@register.filter
def in_category(things, category):
    return things.filter(parfum_id=int(category))

@register.filter
def count(things,category):
    return things.filter(parfum_id=int(category)).count()

@register.filter
def count_in_stock(things,category):
    return things.filter(parfum_id=int(category)).exclude(status = 'Todo').count()

@register.filter
def mass(things,category):
    massetotale=0
    for bac in things.filter(parfum_id=int(category)):
        massetotale = massetotale + bac.poids
    return massetotale

@register.filter
def in_category2_dispo(things, category):
    return things.filter(parfum_text=category, status = 'Disponible').count()

@register.filter
def status_value(things, category):
    return things.filter(status=category).order_by('date_prod')

@register.filter
def count_disponible(things,category):
    return things.filter(parfum_id=int(category), status='Disponible').count()

@register.filter
def count_todo2(things,category):
    return things.filter(parfum_id=int(category), status='Todo').count()

@register.filter
def count_todo(things):
    return things.filter(status='Todo').count()

@register.filter
def count_ordered(things,category):
    return things.filter(parfum_id=int(category), status='Ordered').count()

@register.simple_tag
def count_ordered_by_franchise(things,category,franchise):
    return things.filter(parfum_id=int(category), franchise_name=franchise).exclude(status = 'Disponible').count()

@register.filter
def mass_disponible(things,category):
    massetotale=0
    for bac in things.filter(parfum_id=int(category), status='Disponible'):
        massetotale = massetotale + bac.poids
    return massetotale
    
@register.filter
def count_command(things,category):
    return things.filter(parfum_id=int(category)).exclude(status = 'Disponible').count()

@register.filter
def count_ordered_by_franchise_parfum(user,parfum):
    nb = Glace.objects.filter(parfum_id = int(parfum), franchise_name = user).exclude(status='Disponible').count()
    if nb != 0:
        return int(nb)
    else :
        return 0

@register.filter
def extract_order_date(things):
    order_list=[]
    for g in things.exclude(status='Disponible'):
        order_list.append(g.commande_time.strftime("%Y-%m-%d %H:%M:%S"))
    order_list=list(set(order_list))
    return order_list

@register.filter
def date_formater(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")
"""
@register.filter
def extract_franchise(date, bdd):
    print(date,bdd)
    print(bdd.filter(commande_time = date).exclude(status='Disponible'))
    return True
"""