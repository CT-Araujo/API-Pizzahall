
from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from uuid import uuid4

from rest_framework.response import Response
from rest_framework import status

class UserManager(BaseUserManager):
    def create_user(self, email, isCliente, isGoogle, googleId, password):
        fields =  [email, isCliente, isGoogle, password]
            
        
        for f in fields:
            if f is None or f == '':
                return Response ({"Message":f' O campo {f} não foi informado corretamente.'}, status = status.HTTP_400_BAD_REQUEST)
        
        email = self.normalize_email(email)
        user = self.model( email = email, isCliente = isCliente, isGoogle = isGoogle, googleId = googleId)
        user.set_password(password)
        user.save()
        
        return user  
    
class User (AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(default = uuid4, primary_key= True, editable = False, unique = True,)
    isCliente = models.BooleanField(default = False, editable = False, null = False, blank = False)
    isGoogle = models.BooleanField(default = False, editable = False, null = False, blank = False)
    googleId = models.CharField(blank = True, null = False, max_length = 200)
    email = models.EmailField(unique = True, blank = False, null = False,)
    created = models.DateField(auto_created= True, auto_now_add= True, editable= False)
    
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['isGoogle', 'isCliente']
    objects = UserManager()
    
    
    
class Cliente(models.Model):
    id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key = True)
    nome = models.CharField(max_length = 100, blank = False, null = False,)
    telefone = models.CharField(max_length= 11, unique = False, blank = True, null = True)
    dataNasc = models.DateField(null = True, blank = True)
    cpf = models.CharField(max_length = 14, unique = False, blank = True,null = True, default = None)
    
    
class Pizzarias(models.Model):
    id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key = True)
    nome = models.CharField(max_length = 50, blank = False, null = False)
    status = models.CharField(max_length = 20, default = 'Fechado')
    telefone = models.CharField(max_length = 11, unique = False, blank = False, null = False )
    cnpj = models.CharField(max_length = 14, unique = False, blank = True, null = False, default = None)
    horario = models.CharField(max_length = 100, blank = True, null = True)
    
class Endereco(models.Model):
    id = models.UUIDField(default = uuid4, primary_key = True, editable = False, unique = True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.CharField(max_length = 50)
    cidade = models.CharField(max_length = 100)
    bairro = models.CharField(max_length = 100)
    rua = models.CharField(max_length = 150)
    cep = models.CharField(max_length = 150, )
    numero = models.IntegerField()
    complemento = models.CharField(max_length = 200, blank = True, null = True)

class Produtos(models.Model):
    id = models.UUIDField(default = uuid4, unique = True, primary_key = True)
    pizzaria = models.ForeignKey(Pizzarias, on_delete = models.CASCADE)
    nome = models.CharField(max_length = 40)
    descricao = models.CharField(max_length = 200)
    preco = models.FloatField()