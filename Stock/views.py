from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import FileResponse, HttpResponse   
from .models import Glace, Parfum, Franchise
from .forms import OrderForm, AuthForm, ProdForm, EtiForm, numLotForm
from reportlab.pdfgen import canvas
from django.views.decorators.csrf import csrf_protect
import datetime
from django.forms import BaseFormSet
from django.forms import formset_factory
from django.utils import timezone
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError


def orderSystem(ordered, client):
    for p, n_order in ordered.items():
        dispo = Glace.objects.filter(parfum_text = p, status = "Disponible").count()
        if dispo >= n_order:
            # Ligne de dessous interdite solution possible : https://stackoverflow.com/questions/35206482/cannot-update-a-query-once-a-slice-has-been-taken-best-practices/35206976
            #Glace.objects.filter(parfum_text=p, status = 'Disponible').order_by('date_prod')[:n_order].update(status = 'Ordered', franchise_name = client)
            #Mise en place de la solution
            sliced_query = Glace.objects.filter(parfum_text=p, status = 'Disponible').order_by('date_prod')[:n_order]
            Glace.objects.filter(id__in=sliced_query).update(status = 'Ordered', franchise_name = str(client))
        elif dispo == 0:
            for i in range(int(n_order)):
                auto_id = Parfum.objects.filter(parfum_text=p).values('id')
                todo = Glace(parfum_text = p, parfum_id = next(iter(auto_id))['id'] , poids= 0, date_prod = timezone.now(), status = 'Todo', franchise_name = str(client), commande_time = timezone.now())
                todo.save()
        else : 
            diff = int(n_order-dispo)
            Glace.objects.all().filter(parfum_text = p, status = 'Disponible').update(status='Ordered', franchise_name = str(client))
            for i in range(diff):
                auto_id = Parfum.objects.filter(parfum_text=p).values('id')
                todo = Glace(parfum_text = p, parfum_id = next(iter(auto_id))['id'] , poids= 0, date_prod = timezone.now(), status = 'Todo', franchise_name = str(client), commande_time = timezone.now())
                todo.save()


def test(request, parfum_text, number):
    #parfum_BDD = Parfum.objects.all()
    print('ok', parfum_text, number)
    for i in range(int(number)):
        poids = 0
        parfum = parfum_text
        no_lot = '0/0'
        date_prod = datetime.datetime.now()
        auto_id = Parfum.objects.filter(parfum_text=parfum).values('id')
        #On attaque la BDD
        if Glace.objects.filter(status = 'Todo', parfum_text = parfum).count()>0:
            todo_list = Glace.objects.filter(status = 'Todo', parfum_text = parfum).order_by('commande_time')
            id_to_delete = todo_list[0].id
            pre_command_time = todo_list[0].commande_time
            franchise_command = Glace.objects.filter(id=id_to_delete).values('franchise_name')
            new_entry = Glace(parfum_text=parfum, parfum_id=next(iter(auto_id))['id'],commande_time=pre_command_time, poids=poids/1000, date_prod=date_prod,date_dlc = date_prod+datetime.timedelta(6*365/12), no_lot=no_lot, status = 'Ordered', franchise_name = next(iter(franchise_command))['franchise_name'])
            Glace.objects.filter(id=id_to_delete).delete()
        elif Glace.objects.filter(status = 'Todo', parfum_text = parfum).count()== 0:
            new_entry = Glace(parfum_text=parfum, parfum_id=next(iter(auto_id))['id'], poids=poids/1000, date_prod=date_prod,date_dlc =date_prod+datetime.timedelta(6*365/12), no_lot=no_lot)
        new_entry.save()
        
    context={
    }
    return redirect("/fabrication")

def delete_stock(request, bac):
    id_to_delete = int(bac)
    Glace.objects.filter(id=id_to_delete).delete()
    return redirect("/stocks#s2")

def delete_order(request, bac):
    id_to_delete = int(bac)
    Glace.objects.filter(id=id_to_delete).delete()
    return redirect("/commandes")
    
###########################################
##### Landing Page apres une commande #####
###########################################

# def land(request):
#     context = {
#     }
#     return render(request, 'Stock/land.html', context)

class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        self.forms[0].empty_permitted = False

######################
##### Login Page #####
######################

@login_required
def accueil(request):
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    glace_BDD = Glace.objects
    if request.user.is_superuser:
        parfum_BDD = Parfum.objects.all()
    else :
        parfum_BDD = Parfum.objects.all().exclude(parfum_text__contains='Soft')
    franchise_BDD = User.objects.filter(groups__name='Franchises')
    form2 = OrderForm(questions= parfum_BDD.filter(sorbet=True).order_by('parfum_text'))
    form2b = OrderForm(questions= parfum_BDD.filter(sorbet=False).order_by('parfum_text'))
    if request.method == 'POST' and 'order' in request.POST:
        form2 = OrderForm(request.POST, questions=parfum_BDD.order_by('parfum_text').filter(sorbet=True))
        form2b = OrderForm(request.POST, questions=parfum_BDD.order_by('parfum_text').filter(sorbet=False))
        #Vérification de la validité du Form
        if form2.is_valid() and form2b.is_valid():
            #On récupère les data du form
            data1 = form2.cleaned_data
            data2 = form2b.cleaned_data
            data = {**data1, **data2}
            client = request.user

            #Dict des données commandées (si nombre >0)
            ordered = {}
            for parfum, order in data.items():
                if order >0:
                    ordered[parfum] = order
            sujet = "Commandes de " + str(client)
            content = "<div>Salut David, \n Voici les commandes pour" + str(client) + " \n"
            for parfum, order in ordered.items():
                content = content + str(parfum) + ":" +str(order) + "\n"

            # Courriel de confirmation
            subject_confirmed = "Récapitulatif commande auprès de Papilla"
            content_confirmed = "<div>Bonjour, \n Veuillez trouver ci-après la liste des bacs commandés. \n"
            for parfum, order in ordered.items():
                content_confirmed = content_confirmed + str(parfum) + ":" +str(order) + "\n"
            content_confirmed += "\n En cas de souci concernant la commande effectuée, contactez rapidement David au .... \n"

            orderSystem(ordered, client)

        #On envoie vers la landing page
        messages.info(request, 'Votre commande a bien été transmise ! \n Un email récapitulatif de votre commande vous a été envoyé.')
        try:
            send_mail(sujet, content, 'ed.lenotre@gmail.com' ,['spongebob99@yopmail.com'])
            print("DEBUG ========> MAIL ENVOYE")
            # Envoi courriel confirmation
            print(client.email)
            send_mail(subject_confirmed, content_confirmed, 'Papilla Commande', [client.email])

        except BadHeaderError:
            return HttpResponse('Invalid header found.')
    context = {
        'today' : today,
        'glace_BDD' : glace_BDD.order_by('-status','date_prod'),
        'parfum_BDD' : parfum_BDD.order_by('parfum_text'),
        'franchise_BDD' : franchise_BDD,
        'form2' : form2,
        'form2b' : form2b,
        'utilisateur' : request.user.username
    }
    return render(request, 'Stock/accueil.html', context)

@user_passes_test(lambda u: u.is_superuser)
def stocks(request):
    form = formset_factory(ProdForm, extra=1)
    formset = form()
    parfum_BDD = Parfum.objects.all()
    glace_BDD = Glace.objects
    franchise_BDD = User.objects.filter(groups__name='Franchises')
    form4 = ProdForm()
    if request.method == 'POST' and 'b-send' in request.POST:

        # New version #
        form = formset_factory(ProdForm,formset=RequiredFormSet)
        formset = form(request.POST)
        #Le formulaire est ok ?
        print(formset.is_valid())
        print(formset.errors) #Ligne de Debug
        for f in formset:
            print(f.data)
            print(f.cleaned_data.get('poids'))

            if f.is_valid():
                poids = f.cleaned_data['poids']
                parfum = f.cleaned_data['parfum_text']
                print(parfum, 'passé')

                no_lot = f.cleaned_data['no_lot']
                date_prod = f.cleaned_data['date_prod']
                #On récupère l'id en fonction du parfum choisi
            
                print("p="+str(Parfum.objects.filter(id=parfum)[0]))
                auto_id = parfum
                print(auto_id)
                #On attaque la BDD
                if Glace.objects.filter(status = 'Todo', parfum_text = parfum).count()>0:
                    todo_list = Glace.objects.filter(status = 'Todo', parfum_text = parfum).order_by('commande_time')
                    id_to_delete = todo_list[0].id
                    franchise_command = Glace.objects.filter(id=id_to_delete).values('franchise_name')
                    new_entry = Glace(parfum_text=str(Parfum.objects.filter(id=parfum)[0]), parfum_id=auto_id, poids=poids/1000, date_prod=date_prod, date_dlc = date_prod+datetime.timedelta(6*365/12),no_lot=no_lot, status = 'Ordered', franchise_name = next(iter(franchise_command))['franchise_name'])
                    Glace.objects.filter(id=id_to_delete).delete()
                elif Glace.objects.filter(status = 'Todo', parfum_text = parfum).count()== 0:
                    new_entry = Glace(parfum_text=str(Parfum.objects.filter(id=parfum)[0]), parfum_id=auto_id, poids=poids/1000, date_prod=date_prod, date_dlc = date_prod+datetime.timedelta(6*365/12), no_lot=no_lot)
                new_entry.save()
                messages.info(request, 'Les bacs ont été ajoutés aux stocks !')
            #On régénère le form (Peut-être pas nécessaire en fait)
            form = formset_factory(ProdForm, extra=1)
            formset = form()
        #On envoie vers la landing page
        #return redirect('land')
    context = {
        'glace_BDD' : glace_BDD.order_by('parfum_text','poids','date_prod'),
        'parfum_BDD' : parfum_BDD.order_by('parfum_text'),
        'franchise_BDD' : franchise_BDD,
        'form' : formset,
        'form4':form4,
    }
    return render(request, 'Stock/stocks.html', context)

@user_passes_test(lambda u: u.is_superuser)
@csrf_protect
def commandes(request):
    #Instantiation des formulaires
    form2 = OrderForm(questions= Parfum.objects.all().filter(sorbet=True).order_by('parfum_text'))
    form2b = OrderForm(questions= Parfum.objects.all().filter(sorbet=False).order_by('parfum_text'))
    form3 = AuthForm()
    #Référence aux BDD
    parfum_BDD = Parfum.objects.all()
    glace_BDD = Glace.objects
    franchise_BDD = User.objects.filter(groups__name='Franchises')
    
    if request.method == 'POST' and 'order' in request.POST:
        form2 = OrderForm(request.POST, questions=Parfum.objects.all().order_by('parfum_text').filter(sorbet=True))
        form2b = OrderForm(request.POST, questions=Parfum.objects.all().order_by('parfum_text').filter(sorbet=False))
        form3 = AuthForm(request.POST)
        #Vérification de la validité du Form
        if form2.is_valid() and form3.is_valid() and form2b.is_valid():
            #On récupère les data du form
            data1 = form2.cleaned_data
            data2 = form2b.cleaned_data
            data = {**data1, **data2}
            client = form3.cleaned_data['franchise_name']
            #Dict des données commandées (si nombre >0)
            ordered = {}
            for parfum, order in data.items():
                if order >0:
                    ordered[parfum] = order
            orderSystem(ordered, client)
            #On régénère le form (Peut-être pas nécessaire en faite / Si, c'est nécessaire pour clear les data envoyées)
            form2 = OrderForm(questions= Parfum.objects.all().filter(sorbet=True).order_by('parfum_text'))
            form2b = OrderForm(request.POST, questions=Parfum.objects.all().filter(sorbet=False).order_by('parfum_text'))
            form3 = AuthForm()
            messages.info(request, 'Votre commande a bien été envoyée !')
    #Contexte de notre view
    context = {
        'glace_BDD' : glace_BDD.order_by('parfum_text','commande_time'),
        'parfum_BDD' : parfum_BDD.order_by('parfum_text'),
        'franchise_BDD' : franchise_BDD,
        'form2': form2,
        'form2b': form2b,
        'form3': form3,
    }
    return render(request, 'Stock/commandes.html', context)

@user_passes_test(lambda u: u.is_superuser)
def fabrication(request):
    parfum_BDD = Parfum.objects.all()
    glace_BDD = Glace.objects
    franchise_BDD = User.objects.filter(groups__name='Franchises')
    context = {
        'glace_BDD' : glace_BDD.order_by('-status','date_prod'),
        'parfum_BDD' : parfum_BDD.order_by('parfum_text'),
        'franchise_BDD' : franchise_BDD,
    }
    return render(request, 'Stock/fabrication.html', context)

@user_passes_test(lambda u: u.is_superuser)
def etiquettes(request):
    form = EtiForm(questions= Parfum.objects.all().order_by('parfum_text'))
    form2 = numLotForm()
    parfum_BDD = Parfum.objects.all()
    glace_BDD = Glace.objects
    if request.method == 'POST' and 'order' in request.POST:
        form = EtiForm(request.POST, questions=Parfum.objects.all().order_by('parfum_text'))
        form2 = numLotForm(request.POST)
        #Vérification de la validité du Form
        # if form2.is_valid() and form3.is_valid():
        print(form.is_valid())
        print(form2.is_valid())
        print(form2.errors)
        if form.is_valid() and form2.is_valid():
            print('Etiquette Validée')
            data = form.cleaned_data
            data2 = form2.cleaned_data
            print(data)
            etiTodo = {}
            for parfum, number in data.items():
                if number > 0:
                    etiTodo[parfum] = number
            print('Etiquettes à faire : ', etiTodo)
            logo = "http://papilla.fr/wp-content/uploads/2017/02/transpa-1024x474.png"
            response = HttpResponse(content_type='application/pdf')
            filename = 'Lot_n'+data2["n_lot"]+'.pdf'
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
            p = canvas.Canvas(response)
            posX = 0
            posY = 0
            k=0
            print(type(data2["date"]))
            current_date = data2["date"].strftime("%d/%m/%Y")
            dlc_date = (data2["date"]+datetime.timedelta(6*365/12)).strftime("%d/%m/%Y")
            for key in etiTodo:
                for i in range(data[key]):
                    if k>13:
                        k=0
                        p.showPage()
                    if k%2==0:
                        posX = 0
                        posY = 75+(k)*60
                        
                        p.setFont('Helvetica-Bold', 14)
                        p.drawString(posX + 32, posY + 10, str(key))
                        p.setFont('Helvetica', 8)
                        if not Parfum.objects.filter(parfum_text=str(key))[0].sorbet:
                            p.drawString(posX + 2, posY - 8, "Ingrédients :                                    , sucre, crème 35 %MG,                         ," )
                            p.drawString(posX + 2, posY - 16, "dextrose, sirop de glucose déshydraté, maltodextrine, protéines de lait, farine de ")
                            p.drawString(posX+2, posY - 24, "graines de caroube, gomme guar, fibres d’agrumes, __________________")
                            p.setFont('Helvetica-Bold', 8)
                            p.drawString(posX + 48, posY - 8, "lait pasteurisé entier")
                            p.drawString(posX + 214, posY - 8, "lait en poudre")
                        else : 
                            p.drawString(posX+2, posY - 9, "Ingrédients sorbet : Eau, sucre, sirop de glucose déshydraté, dextrose, fructose," )
                            p.drawString(posX +2, posY - 16, "gomme tara, gomme guar, graines de caroube, __________________")
                        p.setFont('Helvetica', 8)                        
                        p.drawString(posX+2, posY - 36, "Produit le : ")
                        p.drawString(posX+2, posY - 46, "DLC : ")
                        p.drawString(posX+2, posY - 56, "N° de Lot : ")
                        p.drawImage(logo, posX+230 ,posY , width=60,height=30,mask='auto')
                        p.drawString(posX, posY + 10, "Parfum : ")
                        p.drawString(posX+44, posY-36, str(current_date))
                        p.drawString(posX+25, posY-46, str(dlc_date))
                        p.drawString(posX+43 , posY-56, str(data2["n_lot"]))
                        p.drawString(posX+150, posY-36, "Conservation : -20°C")
                        p.drawString(posX+150, posY-46, "Poids Net : ")
                        p.setFont('Times-BoldItalic', 8)
                        p.drawString(posX+100, posY-70, "Papilla, 14 Place des Pins, 06740 Châteauneuf-Grasse")
                        
                    else : 
                        posX = 300
                        posY = 75+(k-1)*60
                        print(posX,posY)
                        p.setFont('Helvetica-Bold', 14)
                        p.drawString(posX + 32, posY + 10, str(key))
                        p.setFont('Helvetica', 8)
                        if not Parfum.objects.filter(parfum_text=str(key))[0].sorbet:
                            p.drawString(posX + 2, posY - 8, "Ingrédients :                                    , sucre, crème 35 %MG,                        ," )
                            p.drawString(posX + 2, posY - 16, "dextrose, sirop de glucose déshydraté, maltodextrine, protéines de lait, farine de ")
                            p.drawString(posX+2, posY - 24, "graines de caroube, gomme guar, fibres d’agrumes, __________________")
                            p.setFont('Helvetica-Bold', 8)
                            p.drawString(posX + 48, posY - 8, "lait pasteurisé entier")
                            p.drawString(posX + 214, posY - 8, "lait en poudre")
                        else : 
                            p.drawString(posX+2, posY - 9, "Ingrédients sorbet : Eau, sucre, sirop de glucose déshydraté, dextrose, fructose," )
                            p.drawString(posX +2, posY - 16, "gomme tara, gomme guar, graines de caroube, __________________")
                        p.setFont('Helvetica', 8)                        
                        p.drawString(posX+2, posY - 36, "Produit le : ")
                        p.drawString(posX+2, posY - 46, "DLC : ")
                        p.drawString(posX+2, posY - 56, "N° de Lot : ")
                        p.drawImage(logo, posX+230 ,posY , width=60,height=30,mask='auto')
                        p.drawString(posX, posY + 10, "Parfum : ")
                        p.drawString(posX+44, posY-36, str(current_date))
                        p.drawString(posX+25, posY-46, str(dlc_date))
                        p.drawString(posX+43 , posY-56, str(data2["n_lot"]))
                        p.drawString(posX+150, posY-36, "Conservation : -20°C")
                        p.drawString(posX+150, posY-46, "Poids Net : ")
                        p.setFont('Times-BoldItalic', 8)
                        p.drawString(posX+100, posY-70, "Papilla, 14 Place des Pins, 06740 Châteauneuf-Grasse")
                    k=k+1
            p.showPage()  
            p.save()


            
            return response
    context = {
        'form2':form2,
        'form' : form,
        'glace_BDD' : glace_BDD.order_by('-status','date_prod'),
        'parfum_BDD' : parfum_BDD.order_by('parfum_text'),
    }
    return render(request, 'Stock/etiquettes.html', context) 
