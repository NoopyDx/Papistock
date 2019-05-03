from django import forms
from .models import Glace
from datetime import datetime
from django.forms.widgets import SelectDateWidget, TextInput, NumberInput
from .models import Parfum, Franchise
from bootstrap_datepicker_plus import DatePickerInput
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, Field

# Formulaire ajout stock
class ProdForm(forms.Form):
   BDD_PARFUM = []
   choices = [('Sorbet', [(n.id, n.parfum_text) for n in Parfum.objects.all().filter(sorbet=True).order_by('parfum_text')])]+[('Glace', [(n.id, n.parfum_text) for n in Parfum.objects.all().filter(sorbet=False).order_by('parfum_text')])]
   parfum_text = forms.CharField(label="Parfum", required=True,widget=forms.Select(attrs={'class':'form-control'}, choices=choices ))
   no_lot = forms.CharField(label="N° de lot", initial = "", widget=TextInput(attrs={'size':10,'class':'form-control'}))
   poids = forms.IntegerField(label="Poids (g)", initial=1000, widget=NumberInput(attrs={'size':3,'class':'form-control span2'}))
   date_prod = forms.DateField(label='Date de production', initial = datetime.now(), widget=DatePickerInput(format='%d/%m/%Y',attrs={'class':'form-control'}))


#Formulaire de commande
#Cette structure permet de générer un nombre de field dépendant de l'attribut 'questions'
class OrderForm(forms.Form):
   def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super(OrderForm, self).__init__(*args, **kwargs)
        #On itère la BDD pour appeler les fields du nom des parfums (pas facile à comprendre)
        iter_BDD = iter(questions)
        for q in questions:
            self.fields[str(next(iter_BDD))] = forms.IntegerField(label = q, initial = 0, min_value=0, widget=forms.TextInput(attrs={'class':'form-control span3'}))


class AuthForm(forms.Form):
   franchise_name = forms.ModelChoiceField(label="Franchise", required = True, queryset=User.objects.filter(groups__name='Franchises'), widget=forms.Select(attrs={'class':'form-control'}))


class EtiForm(forms.Form):
   def __init__(self, *args, **kwargs):
      questions = kwargs.pop('questions')
      super(EtiForm, self).__init__(*args, **kwargs)
      #On itère la BDD pour appeler les fields du nom des parfums (pas facile à comprendre)
      iter_BDD = iter(Parfum.objects.all().order_by('parfum_text'))
      for q in questions:
         self.fields[str(next(iter_BDD))] = forms.IntegerField(label = q, initial = 0, min_value=0, widget=forms.TextInput(attrs={'class':'form-control span3'}))


class numLotForm(forms.Form):
   n_lot = forms.CharField(label="N° de lot", initial = "", widget=TextInput(attrs={'size':10}))
   date = forms.DateField(label='Date', initial = datetime.now(), widget=DatePickerInput(format='%d/%m/%Y',attrs={'class':'form-control'}))