from django.shortcuts import render, redirect
from .forms import MensagemForm, ConfirmacaoForm
from django.http import JsonResponse
from .models import Convidado, Confirmacao
import json
from django.db import transaction

# Página Inicial

def index(request):
    return render (request, 'index.html')

def enviar_mensagem(request):

    sucesso = False

    if request.method == 'POST':
        form = MensagemForm(request.POST)
        if form.is_valid():
            form.save()
            sucesso = True
    
    else:
        form = MensagemForm()

    return render(request, 'index.html', {'form': form, 'sucesso': sucesso})


# Nossa História

def nossa_historia(request):
    return render (request, 'nossa_historia.html')


# Confirmar Presença

def confirmar_presenca(request):
    return render (request, 'confirmar_presenca.html')



def formulario_confirmacao(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = ConfirmacaoForm(request.POST)

        if form.is_valid():
            nome = form.cleaned_data['nome'].strip()
            telefone = form.cleaned_data['telefone'].strip()
            comparecera = form.cleaned_data.get('comparecera', '').strip().upper()
            acompanhantes_raw = form.cleaned_data['acompanhantes']

            try:
                acompanhantes = json.loads(acompanhantes_raw) if acompanhantes_raw else []
            except json.JSONDecodeError:
                acompanhantes = []

            # Verifica se o convidado principal está na lista de convidados
            if not Convidado.objects.filter(nome__iexact=nome).exists():
                return JsonResponse({
                    'status': 'erro',
                    'mensagem': 'Verifique seu nome e tente novamente. Caso o erro persista, entre em contato com os noivos.'
                })

            # Verifica se acompanhantes estão na lista de convidados
            for pessoa in acompanhantes:
                nome_acomp = pessoa.get('nome', '').strip()
                if not Convidado.objects.filter(nome__iexact=nome_acomp).exists():
                    return JsonResponse({
                        'status': 'erro',
                        'mensagem': f"Verifique o nome '{nome_acomp}', caso o erro persista, entre em contato com os noivos."
                    })

            # Nova validação: impede confirmações duplicadas
            if Confirmacao.objects.filter(nome__iexact=nome).exists():
                return JsonResponse({
                    'status': 'erro',
                    'mensagem': 'Você já registrou sua resposta.'
                })

            for pessoa in acompanhantes:
                nome_acomp = pessoa.get('nome', '').strip()
                if Confirmacao.objects.filter(nome__iexact=nome_acomp).exists():
                    return JsonResponse({
                        'status': 'erro',
                        'mensagem': f"O acompanhante '{nome_acomp}' já registrou sua resposta."
                    })

            try:
                with transaction.atomic():
                    # Salva o convidado principal com SIM ou NAO
                    Confirmacao.objects.create(nome=nome, telefone=telefone, comparecera=comparecera)

                    # Salva acompanhantes, sempre com o mesmo comparecera do principal
                    for pessoa in acompanhantes:
                        nome_acomp = pessoa.get('nome', '').strip()
                        telefone_acomp = pessoa.get('telefone', '').strip()
                        Confirmacao.objects.create(nome=nome_acomp, telefone=telefone_acomp, comparecera=comparecera)

            except Exception as e:
                return JsonResponse({
                    'status': 'erro',
                    'mensagem': f'Erro ao registrar confirmação: {str(e)}'
                }, status=500)

            return JsonResponse({
                'status': 'sucesso',
                'mensagem': 'Resposta registrada com sucesso!'
            })

        return JsonResponse({
            'status': 'erro',
            'mensagem': 'Formulário inválido. Entre em contato com os noivos.',
            'erros': form.errors
        }, status=400)

    return render(request, 'confirmar_presenca.html', {'form': ConfirmacaoForm()})