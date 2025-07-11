from django.db import models

class Categoria(models.TextChoices):
    CASA = 'CASA', 'Para o nosso lar'
    LUA_DE_MEL = 'LUA_DE_MEL', 'Para nossa lua de mel'

class Subcategoria(models.TextChoices):
    UTENSILIOS = 'UTENSILIOS', 'Utensílios de cozinha'
    ELETRO = 'ELETRO', 'Eletrodomésticos e Eletroportáteis'
    CAMA_MESA_BANHO = 'CAMA_MESA_BANHO', 'Itens cama, mesa e banho'
    MOVEIS = 'MOVEIS', 'Móveis'
    PASSEIOS = 'PASSEIOS', 'Passeios'
    REFEICOES = 'REFEICOES', 'Refeições'
    PASSAGENS = 'PASSAGENS', 'Passagens'
    HOSPEDAGENS = 'HOSPEDAGENS', 'Hospedagens'

class Produto(models.Model):
    nome = models.CharField(max_length=200)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    foto = models.ImageField(upload_to='produtos/')
    categoria = models.CharField(max_length=20, choices=Categoria.choices, default=Categoria.CASA)
    subcategoria = models.CharField(max_length=40, choices=Subcategoria.choices, blank=True, null=True)
    cotas = models.PositiveIntegerField(null=True, blank=True)
    foi_comprado = models.BooleanField(default=False)


    def __str__(self):
        return self.nome

    def cotas_vendidas(self):
        from .models import ItemPedido
        vendidos = ItemPedido.objects.filter(produto=self).aggregate(total=models.Sum('quantidade'))['total']
        return vendidos or 0

    @property
    def cotas_disponiveis(self):
        if self.cotas is None:
            return 0 if self.foi_comprado else 1
        vendidos = self.cotas_vendidas()
        return max(self.cotas - vendidos, 0)

class Pedido(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True)
    nome_cliente = models.CharField(max_length=200)
    email_cliente = models.EmailField()
    telefone_cliente = models.CharField(max_length=30)
    cpf_cliente = models.CharField(max_length=14)

    def __str__(self):
        return f'Pedido {self.id} - {self.nome_cliente}'

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome}'