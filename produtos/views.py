from django.shortcuts import render, redirect, get_object_or_404
import mercadopago
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Produto, Categoria, Pedido, ItemPedido
from django.urls import reverse



def lista_presentes(request):

    produtos_casa = Produto.objects.filter(categoria=Categoria.CASA)
    produtos_lua_de_mel = Produto.objects.filter(categoria=Categoria.LUA_DE_MEL)
    carrinho = request.session.get('carrinho', {})
    total_itens = sum(item['quantidade'] for item in carrinho.values())

    for produto in produtos_casa:
        produto.cotas_restantes = produto.cotas_disponiveis

    for produto in produtos_lua_de_mel:
        produto.cotas_restantes = produto.cotas_disponiveis

    return render(request, 'lista_presentes.html', {
        'produtos_casa': produtos_casa,
        'produtos_lua_de_mel': produtos_lua_de_mel,
        'total_itens_carrinho': total_itens
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
    cotas_restantes = produto.cotas_disponiveis

    if cotas_restantes == 0:
        # Produto indisponível para compra
        return redirect('lista_presentes')  # ou mensagem para o usuário

    carrinho = request.session.get('carrinho', {})
    produto_id_str = str(produto_id)

    quantidade_no_carrinho = carrinho.get(produto_id_str, {}).get('quantidade', 0)
    if quantidade_no_carrinho >= cotas_restantes:
        # Já está no máximo permitido no carrinho
        return redirect('carrinho')

    if produto_id_str in carrinho:
        carrinho[produto_id_str]['quantidade'] += 1
    else:
        carrinho[produto_id_str] = {
            'nome': produto.nome,
            'preco': float(produto.preco),
            'quantidade': 1,
            'foto': produto.foto.url,
            'cotas': produto.cotas
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


sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

def finalizar_compra(request):
    carrinho = request.session.get('carrinho', {})
    dados = request.session.get('dados_usuario', {})

    if not carrinho or not dados:
        return redirect('carrinho')

    items = []
    for item in carrinho.values():
        items.append({
            "title": item['nome'],
            "quantity": item['quantidade'],
            "currency_id": "BRL",
            "unit_price": float(item['preco'])
        })

    ngrok_url = "https://35cc6e99cd37.ngrok-free.app"  # REMOVER APÓS TESTES

    preference_data = {
        "items": items,
        "payer": {
            "email": "test_user_1551517350@testuser.com"    #ALTERAR PARA dados.get('email')
        },
        "payment_methods": {
            "installments": 12
        },
        "back_urls": {
            "success": f"{ngrok_url}/carrinho/etapa4/",      #ALTERAR PARA URL CERTA
            "failure": f"{ngrok_url}/erro-pagamento/",       #ALTERAR PARA URL CERTA
        },
        "auto_return": "approved",
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response.get("response", {})
    init_point = preference.get('init_point')
    sandbox_link = preference.get("sandbox_init_point")

    if not init_point:
        print("Erro ao criar preferência:", preference_response)
        return redirect('erro_pagamento')

    return redirect(sandbox_link)       #ALTERAR PARA init_point


def etapa4(request):
    payment_id = request.GET.get('payment_id') or request.GET.get('collection_id')

    if not payment_id:
        return redirect('erro_pagamento')

    carrinho = request.session.get('carrinho', {})
    dados = request.session.get('dados_usuario', {})
    if not carrinho or not dados:
        return redirect('carrinho')

    # Cria o Pedido
    pedido = Pedido.objects.create(
        nome_cliente=dados.get('nome'),
        email_cliente=dados.get('email'),
        telefone_cliente=dados.get('telefone'),
        cpf_cliente=dados.get('cpf')
    )

    # Cria Itens do Pedido e ajusta cotas
    for produto_id_str, item in carrinho.items():
        produto = get_object_or_404(Produto, id=int(produto_id_str))
        qtd = item['quantidade']

        # Verifica disponibilidade ainda!
        if qtd > produto.cotas_disponiveis:
            return redirect('carrinho')

        # Cria ItemPedido
        ItemPedido.objects.create(
            pedido=pedido,
            produto=produto,
            quantidade=qtd
        )

        # Ajusta cotas se houver
        if produto.cotas:
            if produto.cotas_vendidas() >= produto.cotas:
                produto.foi_comprado = True
        else:
            produto.foi_comprado = True

        produto.save()

    total = sum(item['preco'] * item['quantidade'] for item in carrinho.values())

    # Envia e-mails
    assunto = 'Novo pedido realizado no site'
    destinatario = ['matheuspontessiqueira@gmail.com']

    conteudo = render_to_string('email_pedido.html', {
        'dados': dados,
        'carrinho': carrinho,
        'total': total,
    })

    send_mail(
        assunto,
        '',
        settings.DEFAULT_FROM_EMAIL,
        destinatario,
        html_message=conteudo,
    )

    email_usuario = dados.get('email')
    if email_usuario:
        conteudo_usuario = render_to_string('email_usuario.html', {
            'dados': dados,
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
        'carrinho': {},
        'total': 0,
        'dados': dados
    })

def erro_pagamento(request):
    return render(request, 'erro_pagamento.html')
