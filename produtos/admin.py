from django.contrib import admin
from .models import Produto, ItemPedido

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco', 'cotas')
    list_filter = ('categoria',)
    search_fields = ('nome',)

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    search_fields = ('nome',)