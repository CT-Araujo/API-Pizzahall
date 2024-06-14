from rest_framework import status
from rest_framework.response import Response
from pycpfcnpj import cpfcnpj
import requests
from .models import Cliente, Pizzarias


def CheckPassword(senha):
    if len(str(senha)) < 8:
        return "Senha muito curta"
    
    maiusculas = sum(1 for s in senha if s.isupper())
    minusculas = sum(1 for s in senha if s.islower())
    numericos = sum(1 for s in senha if s.isnumeric())
            
    result = {"maiusculo":maiusculas, "minúsculo":minusculas, "numérico":numericos}
    
    erros = []
    for c, v in result.items():
        if v == 0:
            erros.append(f"Senha deve conter pelo menos um caractere {c}")
    if len(erros) == 0:
        return True
    else:
        return erros
        
        
    
from rest_framework_simplejwt.tokens import RefreshToken  

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'access': str(refresh.access_token),
    }



def CheckCpf(cpf):
    if str(cpf) == None or str(cpf) == '':
        return True
    else:
        if cpfcnpj.validate(str(cpf)):
            if Cliente.objects.filter(cpf = cpf).exists():
                return False
            else:
                return True
        else:
            return False
        
def Check_cnpj(cnpj):
    if str(cnpj) == None or str(cnpj) == '':
        return True
    else:
        if cpfcnpj.validate(str(cnpj)):
            if Pizzarias.objects.filter(cnpj = cnpj).exists():
                return False
            else:
                return True
        else:
            return False

def ValidaCep(cep):
    if len(str(cep)) < 8:
        return Response({"Message":"CEP inválido, informe um CEP com 8 digitos numéricos"}, status = status.HTTP_400_BAD_REQUEST)
    
    url = f"https://viacep.com.br/ws/{str(cep)}/json/"
    
    response = requests.get(url)
    
    if 'erro' in response.json():
        return Response({"Message":"O CEP informado não corresponde a nenhuma localidade."}, status = status.HTTP_400_BAD_REQUEST)
    
    return Response(response.text, status = status.HTTP_200_OK)