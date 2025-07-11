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

    def __str__(self):
        return self.nome