from django.db import models

class Mensagem(models.Model):
    nome = models.CharField(max_length=100)
    mensagem = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nome} - {self.data_envio.strftime("%d/%m/%Y")}'
    

#Lista de Convidados

class Convidado(models.Model):
    nome = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nome


class Confirmacao(models.Model):
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20)
    comparecera = models.CharField(max_length=3, choices=[('SIM', 'Sim'), ('NAO', 'Não')])

    def __str__(self):
        return f"{self.nome} - {self.comparecera}"