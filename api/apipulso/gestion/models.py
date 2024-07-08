from django.db import models
from django.utils import timezone
from pulso.models import Placa

# Create your models here.






# Create your models here.

# Modulo Auxiliar

    

class pais (models.Model):
    id_pais= models.AutoField(
        primary_key=True
    )
    nombre= models.TextField(
        null=False,
        max_length=150)
    
class provincia (models.Model):
    id_provincia= models.AutoField(
        primary_key=True
    )
    nombre_provincia= models.TextField(null=False,
                                       max_length=150)
    codigo_provincia= models.TextField(null=False,
                                       max_length=6)
    pais_idpais= models.ForeignKey(pais , on_delete=models.PROTECT)

class localidad (models.Model):
    id_localidad= models.AutoField(
        primary_key=True
    )
    nombre_localidad = models.TextField(null=False,
                                       max_length=150)
    cp_localidad= models.TextField(null=False,
                                       max_length=10)
    provincia_id_provincia = models.ForeignKey(provincia, on_delete=models.PROTECT)

class tipo_documento (models.Model):
    idtipo_documento= models.AutoField(
        primary_key=True
    )
    descripcion=models.TextField(null=False,
                                 max_length=150)
    cod_afip=models.IntegerField(null=False)

class situacionIva (models.Model):
    idsituacionIva= models.AutoField(
        primary_key=True
    )
    descripcion=models.TextField(null=False,
                                 max_length=150)
    reducida=models.TextField(null=False,
                              max_length=10)

class tipo_cuenta (models.Model):
    id_tipo_cuenta= models.AutoField(
        primary_key=True
    )
    descripcion=models.TextField(null=False,
                                 max_length=150)
    
#cuenta gestiona proveedores / clientes

class cuenta (models.Model):
    id_cuenta=models.AutoField(
        primary_key=True)
    
    nombre_cuenta =models.TextField(
        null=False, 
        blank=False, max_length=150)
    numero_documento = models.TextField(
        null=False, 
        blank=False, max_length=15)
    
    direccion_cuenta = models.TextField(
        null=False, 
        blank=False, max_length=200)
    
    telefono_cuenta = models.TextField(
        null=True, 
        blank=True, max_length=15)
    
    email_cuenta = models.TextField(
        null=True, 
        blank=True, max_length=150)
    
    celular_cuenta = models.TextField(
        null=True, 
        blank=True, max_length=15)
    
    tipo_documento_idtipo_documento = models.ForeignKey(
        tipo_documento,
        null=True, 
        blank=False, 
        on_delete=models.PROTECT)
    
    pais_id = models.ForeignKey(
        pais,
        on_delete=models.PROTECT, 
        null=True, blank=True)
    
    provincia_idprovincia = models.ForeignKey(
        provincia,
        null=True, 
        blank=False,
        on_delete=models.PROTECT)
    
    localidad_idlocalidad = models.ForeignKey( 
        localidad,
        null=True, 
        blank=False,
        on_delete=models.PROTECT)
    
    tipo_cuenta_id_tipo_cuenta = models.ForeignKey( 
        tipo_cuenta,
        null=True, 
        blank=False,
        on_delete=models.PROTECT)
    
    
    situacionIva_idsituacionIva =models.ForeignKey( 
        situacionIva,
        null=True, 
        blank=False,
        on_delete=models.PROTECT)

class artefacto(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion=models.CharField(
        null=False,
        blank=False,
        max_length=200
    )

class Cuenta_has_Artefacto(models.Model):
    id = models.AutoField(primary_key=True)
    cuenta=models.ForeignKey(
        cuenta,
        null=False,
        blank=False,
        on_delete=models.PROTECT
    )
    artefacto=models.ForeignKey(
        artefacto,
        null=False,
        blank=False,
        on_delete=models.PROTECT
    )
    placa=models.ForeignKey(
        Placa,
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )