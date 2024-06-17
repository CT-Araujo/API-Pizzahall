from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse
import requests
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from google.oauth2 import id_token

#from projeto.settings import GOOGLE_OAUTH2_CLIENT_ID
from .serializers import ClienteSerializers, LoginSerializers, PatchUsuarios, PizzariaSerializers,PacthPizzarias, EnderecoSerializers, ProdutosSerialziers, PedidosSerializers
from .models import Cliente, User, Pizzarias, Endereco, Produtos, Pedidos
from .validators import CheckPassword, get_tokens_for_user, CheckCpf, Check_cnpj, ValidaCep
from .transactions import PagamentoPix


class ClienteViews(APIView):    
    def get(self, request):
        filtro = request.query_params.get('id', None)
        address = request.query_params.get('address', None)
        
        if filtro:
            try:
                cliente = Cliente.objects.get(id= filtro)
                user = cliente.id
            except Cliente.DoesNotExist:
                return Response({"Message":"Usuário não encontrado."}, status = status.HTTP_404_NOT_FOUND)
            
            if address == 'True':
                endereco = Endereco.objects.filter(user_id = cliente.id)
                
                endereco_data = [{
                    "id":e.id,
                    "estado": e.estado,
                    "cidade": e.cidade,
                    "bairro": e.bairro,
                    "rua": e.rua,
                    "cep": e.cep,
                    "numero": e.numero,
                    "complemento": e.complemento
                    } for e in endereco]
                
                user_data = {
                    "id": user.id,
                    "email": user.email,
                    "isGoogle": user.isGoogle,
                    "nome": cliente.nome,
                    "telefone": cliente.telefone,
                    "cpf": cliente.cpf,
                    "dataNasc": cliente.dataNasc 
                }
                
                dados = {
                    "user": user_data,
                    "endereco": endereco_data
                }
                
            else:
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
        
        user = Cliente.objects.all()
        dados = [{
            "id": cliente.id.id,
            "email": cliente.id.email,
            "nome": cliente.nome,
            "telefone": cliente.telefone,
            "cpf": cliente.cpf,
            "dataNasc": cliente.dataNasc
            }for cliente in user]
        
        return Response(dados, status = status.HTTP_200_OK)
    

    def post(self, request):
        serialized = ClienteSerializers(data = request.data)
        
        if serialized.is_valid():
            email = serialized.validated_data.get('email')
            password = serialized.validated_data.get('password')
            
            if CheckPassword(password) == True:
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
            return Response(CheckPassword(password), status = status.HTTP_400_BAD_REQUEST)
        return Response(serialized.errors, status = status.HTTP_400_BAD_REQUEST)
    
    
    def patch(self, request):
        filtro = request.query_params.get('id', None)
        
        if filtro:
            try:
                user = User.objects.get(id = filtro)
                pizzaria = Cliente.objects.get(id_id = filtro)    
            except ObjectDoesNotExist:
                return Response({"Message": "Usuário não encontrado."}, status = status.HTTP_404_NOT_FOUND)
            
            serializer = PatchUsuarios(data = request.data)
            
            if serializer.is_valid():
                email = serializer.validated_data.get('email')
                
                if email is not None and email != "":
                    if User.objects.filter(email = email).exists():
                        return Response({"Message":"Email já cadastrado no banco de dados."}, status = status.HTTP_404_NOT_FOUND)
                    
                    user.email = email
                    user.save()
                    
                patching = PatchUsuarios(pizzaria, data = request.data, partial = True)
                if patching.is_valid():
                    cpf = serializer.validated_data.get('cpf')
                    if cpf != None and cpf != "":
                        if CheckCpf(cpf):
                            
                            if Cliente.objects.filter(cpf = cpf).exists():
                                return Response({"Message":"CPF já em uso."}, status = status.HTTP_400_BAD_REQUEST)
                            else:
                                patching.save()
                            return Response({"Message": "Dados alterados com sucesso."}, status = status.HTTP_202_ACCEPTED)
                        
                        return Response({"Message":"CPF inválido"}, status = status.HTTP_400_BAD_REQUEST)
                    patching.save()
                    return Response({"Message": "Dados alterados com sucesso."}, status = status.HTTP_202_ACCEPTED)
                return Response(patching.errors, status = status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        
        return Response({"Message":"Filtro inválido ou não informado."}, status = status.HTTP_400_BAD_REQUEST)
    
             
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

'''class GoogleAuthenticationView(APIView):
    def post(self, request):
        serializers = GoogleSerializers( data = request.data)
        if serializers.is_valid():
            token = serializers.validated_data.get('token_google')  # Supondo que o token seja enviado no corpo da solicitação.

            if not token:
                return Response({'error': 'Token não fornecido.'}, status=400)

            try:
                id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_OAUTH2_CLIENT_ID)
                password = id_info['sub']
                email = id_info.get('email')
                
                user = serializers.create(serializers.validated_data)
                if user:
                    token = get_tokens_for_user(email, password)
                    user_data = User.objects.get(email = email)
                    if token:
                        login = {
                            "token": token,
                            "id": user_data.id,
                        }
                        return Response(login, status = status.HTTP_201_CREATED)
                    return Response({"message":"Erro na criação do token"}, status = status.HTTP_400_BAD_REQUEST)
                return Response(status = status.HTTP_401_UNAUTHORIZED)  

            except ValueError as e:
                return Response({'error': f'Token inválido: {str(e)}'}, status=400)
        return Response(status = status.HTTP_400_BAD_REQUEST)        
    '''

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class PizzariasViews(APIView):
    def get(self, request):
        filtro = request.query_params.get('id', None)
        address = request.query_params.get('address', None)
        
        if filtro:
            try:
                pizzaria = Pizzarias.objects.get(id = filtro)
                user = pizzaria.id
            except Pizzarias.DoesNotExist:
                return Response({"Message":"Usuário não encontrado"}, status = status.HTTP_404_NOT_FOUND)
            
            if address == 'True':
                print('foi')                
                endereco = Endereco.objects.filter(user_id = user)
                
                endereco_data = [{
                    "id":e.id,
                    "estado": e.estado,
                    "cidade": e.cidade,
                    "bairro": e.bairro,
                    "rua": e.rua,
                    "cep": e.cep,
                    "numero": e.numero,
                    "complemento": e.complemento
                    } for e in endereco]
                
                pizzaria_data = {
                    "id": user.id,
                    "nome": pizzaria.nome,
                    "email": user.email,
                    "telefone": pizzaria.telefone,
                    "horario": pizzaria.horario
                }
                
                dados = {
                    "pizzaria":pizzaria_data,
                    "endereco": endereco_data
                }
                return Response(dados, status = status.HTTP_200_OK)
            
            dados = {                
                "id": user.id,
                "nome": pizzaria.nome,
                "email": user.email,
                "telefone": pizzaria.telefone,
                "horario": pizzaria.horario
            }
            return Response(dados, status = status.HTTP_200_OK)
        
        dados = Pizzarias.objects.all()
        retornado = [{
                "id": pizzaria.id.id,
                "nome": pizzaria.nome,
                "email": pizzaria.id.email,
                "telefone": pizzaria.telefone,
                "horario": pizzaria.horario
            } for pizzaria in dados]
        

        return Response(retornado, status = status.HTTP_200_OK)
        
    def post(self, request):
        serializer = PizzariaSerializers(data = request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            cnpj = serializer.validated_data['cnpj']
            telefone = serializer.validated_data['telefone'] # Será usado para validar o telefone informado pelo usuário.
            
            if CheckPassword(password) == True:
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
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    
    
    def patch(self, request):
        filtro = request.query_params.get('id', None)
        if filtro:
            try:
                
                user = User.objects.get(id = filtro)
                cliente = Pizzarias.objects.get(id_id = filtro)    
                
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
                    
                patching = PacthPizzarias(cliente, data = request.data, partial = True)
                
                if patching.is_valid():
                    cnpj = serializer.validated_data['cnpj']
                    if cnpj is not None and cnpj != "":
                        if Check_cnpj(cnpj):
                            if Pizzarias.objects.filter(cnpj = cnpj).exists():
                                return Response({"Message":"CNPJ já em uso."}, status = status.HTTP_400_BAD_REQUEST)
                            else:  
                                patching.save()
                                return Response({"Message": "Dados alterados com sucesso."}, status = status.HTTP_202_ACCEPTED)
                    patching.save()
                    return Response({"Message": "Dados alterados com sucesso."}, status = status.HTTP_201_CREATED)
                    
                return Response(patching.errors, status = status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        return Response({"Message":"Filtro inválido ou não informado."}, status = status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        get_id = request.query_params.get('id',None)
        try: 
            dado = User.objects.filter(id= get_id).first()
            dado.delete()
            return Response(status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
           
class EnderecoViews(APIView):
    def get(self, request):
        filtro = request.query_params.get('id', None)
        if filtro:
            print('com filtro')
            
            enderecos = Endereco.objects.filter(user = filtro)
            if len(enderecos) == 0:
                return Response({"Message":"Nenhum endereço encontrado neste usuário"}, status = status.HTTP_404_NOT_FOUND)
            
            serializer = EnderecoSerializers(enderecos, many = True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        
        dados = Endereco.objects.all()
        serializer = EnderecoSerializers(dados, many = True)
        print('sem filtro')
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    
    def post(self, request):
        serializer = EnderecoSerializers(data = request.data)
        
        if serializer.is_valid():
            cep = serializer.validated_data['cep']
            if ValidaCep(cep).status_code != 400:
                if Endereco.objects.filter(user = serializer.validated_data['user']).count() < 2:
                    new = Endereco.objects.create(
                        user = serializer.validated_data['user'],
                        estado = serializer.validated_data['estado'],
                        cidade = serializer.validated_data['cidade'],
                        bairro = serializer.validated_data['bairro'],
                        rua = serializer.validated_data['rua'],
                        cep = serializer.validated_data['cep'],
                        numero = serializer.validated_data['numero'],
                        complemento = serializer.validated_data['complemento']
                    )
                    
                    new.save()
                    return Response(serializer.data, status = status.HTTP_201_CREATED)
                return Response({"Message":"Já existem 2 endereços cadastrados nesse usuário."}, status = status.HTTP_403_FORBIDDEN)
            return (ValidaCep(cep))
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////   
    
class ProdutosViews(APIView):
    def get(self, request):
        filtro = request.query_params.get('pizzaria', None) 
        unico = request.query_params.get('id', None)
        
        if filtro:
            produto = Produtos.objects.filter(pizzaria_id = filtro)
            serializers = ProdutosSerialziers(produto, many = True)
            print(produto)
            return Response(serializers.data, status = status.HTTP_200_OK)
        
        if unico:
            produto = Produtos.objects.filter(id = unico)
            serializers = ProdutosSerialziers(produto, many = True)
            return Response(serializers.data, status = status.HTTP_200_OK)
        
        dados = Produtos.objects.all()
        serializers = ProdutosSerialziers(dados, many = True)
        return Response(serializers.data, status = status.HTTP_200_OK)
    
    def post(self, request):
        serializers = ProdutosSerialziers(data = request.data)
        
        if serializers.is_valid():
            # Verificar se realmente é uma pizzaria
            produto = Produtos.objects.create(
                pizzaria = serializers.validated_data['pizzaria'],
                nome = serializers.validated_data['nome'],
                descricao = serializers.validated_data['descricao'],
                opcoes = serializers.validated_data['opcoes']
            )
            
            produto.save()
            return Response(serializers.data, status.HTTP_201_CREATED)
        return Response(serializers.errors, status.HTTP_400_BAD_REQUEST)
    
    def patch(self,request):
        filtro = request.query_params.get('id', None)
        try:
            produto = Produtos.objects.get(id = filtro)
        except ObjectDoesNotExist:
            return Response({"Message":"Produto não encontrado"}, status = status.HTTP_404_NOT_FOUND)
        
        seriliazers = ProdutosSerialziers(produto, partial = True, data = request. data)
        if seriliazers.is_valid():
            
            if seriliazers.validated_data.get('venda') is not None and seriliazers.validated_data.get('venda') != '':
                
                inicial = produto.venda
                add = seriliazers.validated_data.get('venda', [])
    
                inicial.extend(add)
                produto.venda = inicial
                produto.save()
                del seriliazers.validated_data['venda']
                
            seriliazers.save()
            return Response(seriliazers.data, status = status.HTTP_200_OK)
        return Response(seriliazers.erros, status = status.HTTP_400_BAD_REQUEST)


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////   


class PedidosViews(APIView):
    def get(self, request):
        filtro = request.query_params.get('id', None)
        filtro_cliente = request.query_params.get('cliente', None)
        
        if filtro:
            try: 
                pedido = Pedidos.objects.get(id = filtro)
                if pedido:
                    pizzaria = Pizzarias.objects.get(id = pedido.pizzaria.id)
            except Pedidos.DoesNotExist:
                return Response({"Message":"Pedido não encontrado."}, status = status.HTTP_404_NOT_FOUND)
            dado = {
                "id": pedido.id,
                "cliente": pedido.cliente.id,
                "pizzaria": pedido.pizzaria.id,
                "nome_pizzaria": pizzaria.nome,
                "produto":pedido.produtos,
                "precoInicial":pedido.precoInicial,
                "precoFinal":pedido.precoFinal,
                "status": pedido.status
            }
            return Response(dado, status = status.HTTP_200_OK)
        
        if filtro_cliente:
            try: 
                pedido = Pedidos.objects.filter(cliente = filtro_cliente)
            except Pedidos.DoesNotExist:
                return Response({"Message":"Este usuário não possui nenhum pedido."}, status = status.HTTP_404_NOT_FOUND)
            
            
            serializers = PedidosSerializers(pedido, many = True)
            return Response(serializers.data, status.HTTP_200_OK)
        
        dados = Pedidos.objects.all()
        serializers = PedidosSerializers(dados, many = True)
        return Response(serializers.data, status = status.HTTP_200_OK)
    
    
    def post(self, request):
        serializers = PedidosSerializers(data = request.data)
        if serializers.is_valid():
            try:
                getpz = Pizzarias.objects.get(id = serializers.validated_data.get('pizzaria'))
            except Pizzarias.DoesNotExist:
                return Response({"Message":"Pizzaria não existe"},status = status.HTTP_404_NOT_FOUND)
            
            if getpz:
                try:
                    endereco = Endereco.objects.get(user = getpz.id)
                
                except Endereco.DoesNotExist:
                    return Response({"Message":"Pizzaria informada não possui um endereço cadastrado"})
            
            try:
                getct = Cliente.objects.get(id = serializers.validated_data.get('cliente') )
            except Cliente.DoesNotExist:
                return Response({"Message":"Cliente não existe"}, status = status.HTTP_404_NOT_FOUND)
            
            precoFinal = serializers.validated_data['precoFinal']
            novo = Pedidos.objects.create(
                cliente = getct.id,
                pizzaria = getpz.id,
                produtos = serializers.validated_data['produtos'],
                precoInicial = serializers.validated_data['precoInicial'],
                precoFinal = precoFinal,
                status = serializers.validated_data['status']   
            )
            
            novo.save()
            
            if novo:
                import math

                if '.' in str(precoFinal) or ',' in str(precoFinal):
                    precoFinal = float(str(precoFinal).replace(',', '.'))
                    total = int(precoFinal * 100)
                else:
                    total = int(precoFinal) * 100

                pagamento = PagamentoPix(getpz.nome, getpz.telefone, endereco.cidade, total)
                return Response(pagamento, status = status.HTTP_200_OK)    
        return Response(serializers.errors, status.HTTP_400_BAD_REQUEST)
    
    
    