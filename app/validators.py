from rest_framework import status
from rest_framework.response import Response
from pycpfcnpj import cpfcnpj
import requests
def CheckPassword(password):
    if len(password) < 8:
        return 'Senha muito curta'
    
    else:
        checks = {
            "min": False,
            "mai": False,
            "num": False
        }
        for p in password:
            if str(p).islower():
                checks['min'] = True
            if str(p).isupper():
                checks['mai'] = True
            if str(p).isnumeric():
                checks['num'] = True
        
        erros = []
        
        if checks['min'] == False:
            erros.append({"Message":"A senha deve conter pelo menos um caracter minusculo."})
        if checks['mai'] == False:
            erros.append({"Message":"A senha deve conter pelo menos um caracter maiusculo."})
        if checks['num'] == False:
            erros.append({"Message":"A senha deve conter pelo menos um caracter númerico."})
            
        if len(erros) >= 1:
            return erros
        else:
            return Response(password, status = status.HTTP_200_OK)
            
    
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
            return True
        else:
            return False
        
def Check_cnpj(cnpj):
    if str(cnpj) == None or str(cnpj) == '':
        return True
    else:
        if cpfcnpj.validate(str(cnpj)):
            return True
        else:
            return False

def ValidaCep(cep):
    if len(str(cep)) < 8:
        return Response({"Message":"CEP inválido, informe um CEP com 8 digitos numericos"}, status = status.HTTP_400_BAD_REQUEST)
    
    url = f"https://viacep.com.br/ws/{str(cep)}/json/"
    
    response = requests.get(url)
    
    if 'erro' in response.json():
        return Response({"Message":"O CEP informado não corresponde a nenhuma localidade."}, status = status.HTTP_400_BAD_REQUEST)
    
    return Response(response.text, status = status.HTTP_200_OK)