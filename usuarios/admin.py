from django.contrib import admin
from .models import Convidado, Confirmacao, Mensagem

admin.site.register(Convidado)
admin.site.register(Mensagem)

@admin.register(Confirmacao)
class ConfirmacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'comparecera')  # Colunas visíveis na listagem
    list_filter = ('comparecera',)                      # Filtro lateral por SIM/NAO
    search_fields = ('nome', 'telefone')                # Campo de busca
