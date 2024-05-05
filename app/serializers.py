from rest_framework import serializers, status
from django.contrib.auth import get_user_model
Usermodel = get_user_model()
from rest_framework.exceptions import ValidationError
from .models import Cliente

class ClienteSerializers(serializers.Serializer):
    
    # Parte que será salva no User ( Responsável por validar os usuários em geral)
    
    confirm = serializers.CharField(max_length = 50)
    password = serializers.CharField(max_length = 50)
    email = serializers.EmailField(max_length = 100)
    isGoogle = serializers.BooleanField(default = False)
    googleId = serializers.CharField(max_length = 200,  allow_blank = True)
    isCliente = serializers.BooleanField(default = False)
    
    # Parte que será salva no Cliente
    
    nome = serializers.CharField(max_length = 50)
    
    
    def validate(self, data):
        if data.get('password') != data.get('confirm'):
            raise ValidationError('As senhas não coincidem.', status.HTTP_400_BAD_REQUEST)
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm', None)
        
        user = Usermodel.objects.create_user(
            email = validated_data['email'],
            isGoogle = validated_data['isGoogle'],
            isCliente = validated_data['isCliente'],
            googleId = validated_data['googleId'],
            password = validated_data['password']
        )
        
        
        user.save()
        return user
class PatchCliente(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'