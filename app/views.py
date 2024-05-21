from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from .serializers import ClienteSerializers, LoginSerializers, PatchUsuarios, PizzariaSerializers,PacthPizzarias
from .models import Cliente, User, Pizzarias
from .validators import CheckPassword, get_tokens_for_user, CheckCpf, Check_cnpj

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
                return Response({"Message":"Usuário base não encontrado"}, status = status.HTTP_404_NOT_FOUND)
                
            serializers = PatchUsuarios(user, data = request.data, partial  = True)
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

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////      
        
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

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


class PizzariasViews(APIView):
    def post(self, request):
        serializer = PizzariaSerializers(data = request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            cnpj = serializer.validated_data['cnpj']
            telefone = serializer.validated_data['telefone'] # Será usado para validar o telefone informado pelo usuário.
            
            if CheckPassword(password).status_code == 200:
                if Check_cnpj(cnpj):
                    new = serializer.create(serializer.validated_data)
                    
                    if new:
                        try:
                            user = User.objects.get(email = email)
                        except ObjectDoesNotExist:
                            return Response({"Message":"Usuário base não encontrado"}, status = status.HTTP_400_BAD_REQUEST)
                        
                        newPizzaria = Pizzarias.objects.create(
                            id = user,
                            nome = serializer.validated_data['nome'],
                            telefone = serializer.validated_data['telefone'],
                            cnpj = serializer.validated_data['cnpj']
                        )
                        
                        newPizzaria.save()
                        if newPizzaria:
                            login = authenticate(username = email, password = password)
                            token = get_tokens_for_user(login)
                            dados = {
                                "id": user.id,
                                "token": token['access']
                            }
                            
                            return Response(dados, status = status.HTTP_200_OK)
                return Response({"Message":"CNPJ informado não é vaálido"}, status = status.HTTP_400_BAD_REQUEST)
            return Response(CheckPassword(password), status = status.HTTP_400_BAD_REQUEST)
        return Response(serializer.error_messages, status = status.HTTP_400_BAD_REQUEST)
    
    
    def patch(self, request):
        filtro = request.query_params.get('id', None)
        
        if filtro:
            try:
                user = User.objects.get(id = filtro)
                pizzaria = Pizzarias.objects.get(id_id = filtro)    
            except ObjectDoesNotExist:
                return Response({"Message": "Usuário não encontrado."}, status = status.HTTP_404_NOT_FOUND)
            
            serializer = PacthPizzarias(data = request.data)
            if serializer.is_valid():
                email = serializer.validated_data.get('email')
                if email is not None and email != "":
                    if User.objects.filter(email = email).exists():
                        return Response({"Message":"Email já cadastrado no banco de dados."}, status = status.HTTP_404_NOT_FOUND)
                    user.email = email
                    user.save()
                    
                patching = PacthPizzarias(pizzaria, data = request.data, partial = True)
                if patching.is_valid():
                    patching.save()
                    return Response({"Message": "Dados alterados com sucesso."}, status = status.HTTP_202_ACCEPTED)
                return Response(patching.errors, status = status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        
        return Response({"Message":"Filtro inválido ou não informado."}, status = status.HTTP_400_BAD_REQUEST)
            
            
            