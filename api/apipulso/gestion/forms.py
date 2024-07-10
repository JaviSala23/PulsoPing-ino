from django import forms
from gestion.models import *
from django.forms.widgets import Widget
from django.forms.widgets import NumberInput
from datetime import date


#Formularios.

class paisModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.nombre
    
class tDocumentoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.descripcion
    
class tCuientaBancariaChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.descripcion
    
class provinciaModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.nombre_provincia

class rubroModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.descripcion
    
class seccionModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.descripcion
    
class SivaModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.descripcion
    
class proveedorModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.nombre_cuenta
    



class FormCuenta(forms.Form):
    id=forms.IntegerField(
        label='ID',
        widget=forms.HiddenInput()
    )
    nombre=forms.CharField(
        label='Nombre',
        
    )
    TipoDocumento=tDocumentoChoiceField(label='Seleccione el tipo de documento', queryset=tipo_documento.objects.all().order_by('descripcion'), to_field_name='idtipo_documento', empty_label='--Seleccione Tipo de Documento--' )
    numeroDocumento=forms.CharField(
        label='Numero Documento / CUIT / CUIL',
        
    )
    TipoIva=SivaModelChoiceField(label='Seleccione situacion de IVA', queryset=situacionIva.objects.all().order_by('descripcion'), to_field_name='idsituacionIva', empty_label='--Seleccione Sitiacion de IVA--' )
    direccion=forms.CharField(
        label='Direccion',
       
    )
    telefono=forms.CharField(
        label='Telefono',
       
    )
    celular=forms.CharField(
        label='Celular',
      
    )
    email=forms.EmailField(
        label='Email',
        
    )
    paises=paisModelChoiceField(label='Seleccione Pais', queryset=pais.objects.all().order_by('nombre'), to_field_name='id_pais', empty_label='--Seleccione Pais--', widget=forms.Select(attrs={"onChange":"cargarProvincia()"}))    
    provincia=forms.ChoiceField(label='Seleccione Provincia', choices="", widget=forms.Select(attrs={"onChange":"cargarLocalidad()"}))
    localidad=forms.ChoiceField(label='Seleccione Localidad',choices="" ,)
    tipoCuenta=forms.IntegerField(label='', initial=1,
        widget=forms.HiddenInput())


class ArtefactoForm(forms.ModelForm):
    class Meta:
        model = artefacto
        fields = ['descripcion']




class CuentaHasArtefactoForm(forms.ModelForm):
    cuenta = forms.ModelChoiceField(queryset=cuenta.objects.all(), label='Cuenta')
    artefacto = forms.ModelChoiceField(queryset=artefacto.objects.all(), label='Artefacto')
    placa = forms.ModelChoiceField(queryset=Placa.objects.all(), label='Placa', required=False)

    class Meta:
        model = Cuenta_has_Artefacto
        fields = [
            'cuenta',
            'artefacto',
            'placa',
            'puerto',
            'temp_min',
            'temp_max',
        ]