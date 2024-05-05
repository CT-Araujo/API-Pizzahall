from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from .serializers import ClienteSerializers, PatchCliente, LoginSerializers
from .models import Cliente, User
from .validators import CheckPassword, get_tokens_for_user, CheckCpf

class ClienteViews(APIView):    
    def get(self, request):
        filtro = request.query_params.get('id', None)
        if filtro:
            cliente = Cliente.objects.get(id= filtro)
            user = User.objects.get(id = filtro)
            dados = {
                "id": user.id,
                "email": user.email,
                "isGoogle": user.isGoogle,
                "nome": cliente.nome,
                "telefone": cliente.telefone,
                "cpf": cliente.cpf,
                "dataNasc": cliente.dataNasc 
            }
            
            return Response(dados, status = status.HTTP_200_OK)
    
    def post(self, request):
        serialized = ClienteSerializers(data = request.data)
        
        if serialized.is_valid():
            email = serialized.validated_data.get('email')
            password = serialized.validated_data.get('password')
            
            if CheckPassword(password).status_code == 200:
                creating = serialized.create(serialized.validated_data)
                
                if creating:
                    try:
                        user = User.objects.get(email = email) 
                    except ObjectDoesNotExist:
                        return Response({"Message":"Usuário base não criado corretamente."}, status = status.HTTP_400_BAD_REQUEST)
                    
                    newCliente = Cliente.objects.create(
                        id = user,
                        nome = serialized.validated_data['nome']
                    )
                    
                    newCliente.save()
                    if newCliente:
                        login = authenticate(username = email, password = password)
                        token = get_tokens_for_user(login)
                        
                        dados = {
                            "id": user.id,
                            "token": token['access']
                        }
                        
                        return Response(dados, status = status.HTTP_201_CREATED)
                    return Response({"Message":"Erro ao criar o usuário social."}, status = status.HTTP_400_BAD_REQUEST)
        return Response(serialized.error_messages, status = status.HTTP_400_BAD_REQUEST)
    
    
    def patch(self, request):
        if request.method == 'PATCH':
            id = request.query_params.get('id', None)
            try:
                user = Cliente.objects.get(id = id)
            except ObjectDoesNotExist:
                return Response({"Message":"Usuário não encontrado"}, status = status.HTTP_404_NOT_FOUND)
                
            serializers = PatchCliente(user, data = request.data, partial  = True)
            if serializers.is_valid():
                telefone = serializers.validated_data.get('telefone')
                if CheckCpf(serializers.validated_data.get('cpf')) == True:
                    serializers.save()
                    return Response(serializers.data, status = status.HTTP_200_OK)
                return Response({"Message":"O CPF informado não é válido."}, status = status.HTTP_400_BAD_REQUEST)
            return Response(serializers.errors, status = status.HTTP_400_BAD_REQUEST)
        
             
    # FUNÇÃO APÉNAS PARA A PRODUÇÃO POR QUESTÕES DE AGILIZAR TESTES.
    def delete(self, request):
        get_id = request.query_params.get('id',None)
        try: 
            dado = User.objects.filter(id= get_id).first()
            dado.delete()
            return Response(status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        
class LoginView(APIView):
    def post(self, request):
        serializers = LoginSerializers(data = request.data)
        if serializers.is_valid():
            email = serializers.validated_data.get('email')
            password = serializers.validated_data.get('password')
            
            
            try:
                user = User.objects.get(email = email)
            
            except ObjectDoesNotExist:
                return Response({"Message":"Usuário não cadastrado no nosso sistema."}, status = status.HTTP_404_NOT_FOUND)
            
            login = authenticate(username = email, password = password)
            if login:
                token = get_tokens_for_user(login)
                
                dados = {
                    'token': token['access'],
                    'id': user.id
                }
                
                return Response(dados, status = status.HTTP_200_OK)
            return Response({'Message':'Erro na autenticação'}, status.HTTP_401_UNAUTHORIZED)
        return Response(serializers.error_messages, status = status.HTTP_400_BAD_REQUEST)
    