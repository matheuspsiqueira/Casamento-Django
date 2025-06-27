from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('enviar-mensagem', views.enviar_mensagem, name='enviar_mensagem'),
    path('nossa_historia', views.nossa_historia, name='nossa_historia'),
    path('confirmar_presenca', views.confirmar_presenca, name='confirmar_presenca'),
    path('formulario_confirmacao', views.formulario_confirmacao, name='formulario_confirmacao'),
]