from django.shortcuts import render, redirect, get_object_or_404
import requests
import stripe
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Produto, Categoria
from django.urls import reverse



def lista_presentes(request):

    produtos_casa = Produto.objects.filter(categoria=Categoria.CASA)
    produtos_lua_de_mel = Produto.objects.filter(categoria=Categoria.LUA_DE_MEL)

    return render(request, 'lista_presentes.html', {
        'produtos_casa': produtos_casa,
        'produtos_lua_de_mel': produtos_lua_de_mel,
    })


# ORDENAÇÃO PREÇO


# SUBCATEGORIAS

def filtrar_lua_de_mel(request):
    subcategoria = request.GET.get('subcategoria')
    ordenar = request.GET.get('ordenar')

    produtos = Produto.objects.filter(categoria=Categoria.LUA_DE_MEL)

    if subcategoria and subcategoria != "Todas":
        produtos = produtos.filter(subcategoria=subcategoria)

    if ordenar == 'menor':
        produtos = produtos.order_by('preco')
    elif ordenar == 'maior':
        produtos = produtos.order_by('-preco')

    return render(request, 'partials/_produtos_lua_de_mel.html', {
        'produtos': produtos
    })

def filtrar_nosso_lar(request):
    subcategoria = request.GET.get('subcategoria')
    ordenar = request.GET.get('ordenar')

    produtos = Produto.objects.filter(categoria=Categoria.CASA)

    if subcategoria and subcategoria != "Todas":
        produtos = produtos.filter(subcategoria=subcategoria)

    if ordenar == 'menor':
        produtos = produtos.order_by('preco')
    elif ordenar == 'maior':
        produtos = produtos.order_by('-preco')

    return render(request, 'partials/_produtos_nosso_lar.html', {
        'produtos': produtos
    })


# CARRINHO

def carrinho(request):
    carrinho = request.session.get('carrinho',{})
    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
    return render(request, 'carrinho.html', {'carrinho':carrinho, 'total': total, 'etapa': 1})


def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    carrinho = request.session.get('carrinho', {})

    produto_id_str = str(produto_id)

    if produto_id_str in carrinho:
        if produto.cotas:
            if carrinho[produto_id_str]['quantidade'] < produto.cotas:
                carrinho[produto_id_str]['quantidade'] += 1
        else:
            pass
    else:
        carrinho[produto_id_str] = {
            'nome': produto.nome,
            'preco': float(produto.preco),
            'quantidade': 1,
            'foto': produto.foto.url,
            'cotas':produto.cotas
        }
    
    request.session['carrinho'] = carrinho
    return redirect('carrinho')


def diminuir_quantidade(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)

    if produto_id_str in carrinho:
        if carrinho[produto_id_str]['quantidade'] > 1:
            carrinho[produto_id_str]['quantidade'] -= 1
        else:
            # Se quantidade for 1 e tentar diminuir, mantém em 1 ou remove? Aqui optamos por manter.
            pass

        request.session['carrinho'] = carrinho

    return redirect('carrinho')


def remover_item(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    if str(produto_id) in carrinho:
        del carrinho[str(produto_id)]
        request.session['carrinho'] = carrinho
    return redirect('carrinho')


# ETAPAS

def verificar_carrinho(request):
    carrinho = request.session.get('carrinho', {})
    if not carrinho:
        total = 0
        return render(request, 'carrinho.html', {
            'carrinho': carrinho,
            'total': total,
            'etapa': 1,
            'erro': 'Seu carrinho está vazio.'
        })

    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
    return render(request, 'carrinho.html', {
        'carrinho': carrinho,
        'total': total,
        'etapa': 2
    })

@require_POST
def salvar_dados_etapa2(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        cpf = request.POST.get('cpf').replace('.', '').replace('-', '').strip()

        if not nome or not telefone or not cpf:
            carrinho = request.session.get('carrinho', {})
            total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())
            return render(request, 'carrinho.html', {
                'etapa': 2,
                'carrinho': carrinho,
                'total': total,
                'erro': 'Preencha os campos obrigatórios',
                'dados': {
                    'nome': nome,
                    'email': email,
                    'telefone': telefone,
                    'cpf': cpf
                }
            })

        request.session['dados_usuario'] = {
            'nome': nome,
            'email': email,
            'telefone': telefone,
            'cpf': cpf
        }

        return redirect('etapa3')

    return redirect('etapa2')


def etapa2(request):
    carrinho = request.session.get('carrinho', {})
    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())

    dados_usuario = request.session.get('dados_usuario', {})

    return render(request, 'carrinho.html', {
        'etapa': 2,
        'carrinho': carrinho,
        'total': total,
        'dados': dados_usuario
    })


def etapa3(request):
    carrinho = request.session.get('carrinho', {})
    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())

    return render(request, 'carrinho.html', {
        'etapa': 3,
        'carrinho': carrinho,
        'total': total
    })


def etapa4(request):
    session_id = request.GET.get('session_id')

    if not session_id:
        return redirect('etapa3')
    
    from django.core.cache import cache
    confirmado = cache.get(f'pagamento_{session_id}')
    if not confirmado:
        return render (request, 'erro_pagamento.html')
    
    carrinho = request.session.get('carrinho', {})
    dados_usuario = request.session.get('dados_usuario', {})
    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())

    # Montar conteúdo do e-mail
    assunto = 'Novo pedido realizado no site'
    destinatario = ['matheuspontessiqueira@gmail.com']  # Substitua pelo seu e-mail real

    conteudo = render_to_string('email_pedido.html', {
        'dados': dados_usuario,
        'carrinho': carrinho,
        'total': total,
    })

    # Enviar e-mail
    send_mail(
        assunto,
        '',  # Corpo simples (em branco, já que vamos usar HTML)
        settings.DEFAULT_FROM_EMAIL,
        destinatario,
        html_message=conteudo,
    )

    # E-mail para o comprador, se válido
    email_usuario = dados_usuario.get('email')
    if email_usuario:
        conteudo_usuario = render_to_string('email_usuario.html', {
            'dados': dados_usuario,
            'carrinho': carrinho,
            'total': total,
        })

        send_mail(
            'Seu pedido foi recebido!',
            '',
            settings.DEFAULT_FROM_EMAIL,
            [email_usuario],
            html_message=conteudo_usuario,
        )

    request.session['carrinho'] = {}

    return render(request, 'carrinho.html', {
        'etapa': 4,
        'carrinho': carrinho,
        'total': total,
        'dados': dados_usuario
    })


stripe.api_key = settings.STRIPE_SECRET_KEY

def finalizar_compra(request):
    carrinho = request.session.get('carrinho', {})
    dados = request.session.get('dados_usuario', {})

    if not carrinho or not dados:
        return redirect('carrinho')

    # Monta os produtos
    line_items = []
    for item in carrinho.values():
        line_items.append({
            'price_data': {
                'currency': 'brl',
                'unit_amount': int(item['preco'] * 100),
                'product_data': {
                    'name': item['nome'],
                },
            },
            'quantity': item['quantidade'],
        })

    # Cria uma sessão de checkout
    session = stripe.checkout.Session.create(
        payment_method_types=['card', 'boleto'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri(reverse('aguardando_confirmacao')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('etapa3')),
        customer_email=dados.get('email'),
    )

    # Redireciona para o checkout do Stripe
    return redirect(session.url, code=303)


def aguardando_confirmacao(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('etapa3')
    
    return render(request, 'aguardando_confirmacao.html', {
        'session_id': session_id
    })


def erro_pagamento(request):
    return render(request, 'erro_pagamento.html')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session['id']

        from django.core.cache import cache
        cache.set(f'pagamento_{session_id}', True, timeout=3600)

    return HttpResponse(status=200)


def verificar_pagamento(request):
    session_id = request.GET.get('session_id')
    from django.core.cache import cache
    confirmado = cache.get(f'pagamento_{session_id}')
    return JsonResponse({'confirmado': bool(confirmado)})