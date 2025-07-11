from django.urls import path
from . import views

urlpatterns = [
    path('lista_presentes', views.lista_presentes, name='lista_presentes'),
    path('ajax/filtrar-lua-de-mel/', views.filtrar_lua_de_mel, name='filtrar_lua_de_mel'),
    path('ajax/filtrar-nosso-lar/', views.filtrar_nosso_lar, name='filtrar_nosso_lar'),
    path('carrinho', views.carrinho, name='carrinho'),
    path('adicionar/<int:produto_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/diminuir/<int:produto_id>/', views.diminuir_quantidade, name='diminuir_quantidade'),
    path('remover/<int:produto_id>/', views.remover_item, name='remover_item'),
    path('carrinho/', views.verificar_carrinho, name='verificar_carrinho'),
    path('carrinho/etapa2/', views.etapa2, name='etapa2'),
    path('carrinho/etapa2/salvar/', views.salvar_dados_etapa2, name='salvar_dados_etapa2'),
    path('carrinho/etapa3/', views.etapa3, name='etapa3'),
    path('carrinho/etapa4/', views.etapa4, name='etapa4'),
    path('carrinho/finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path('erro-pagamento/', views.erro_pagamento, name='erro_pagamento'),
]