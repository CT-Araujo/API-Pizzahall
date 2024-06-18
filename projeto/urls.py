
from django.contrib import admin
from django.urls import path
from app.views import ClienteViews, LoginView, PizzariasViews, EnderecoViews, ProdutosViews, PedidosViews, PagamentosViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ClienteViews.as_view(), name = 'cliente'),
    path('login/', LoginView.as_view(), name = 'login'),
    path('pizzarias/', PizzariasViews.as_view(), name = 'pizzarias'),
    path('enderecos/', EnderecoViews.as_view(), name = 'endereco'),
    path('produtos/', ProdutosViews.as_view(), name = 'produtos'),
    path('pedidos/', PedidosViews.as_view(), name = 'pedidos'),
    path('pagamento/', PagamentosViews.as_view(), name ='pagamento')
]

