from django import forms
from .models import Mensagem, Confirmacao, Convidado
import json

#Mensagens deixadas
class MensagemForm(forms.ModelForm):
    class Meta:
        model = Mensagem
        fields = ['nome', 'mensagem']



class ConfirmacaoForm(forms.Form):
    nome = forms.CharField(label='Nome completo', max_length=255)
    comparecera = forms.ChoiceField(
        label='Você irá ao evento?',
        choices=[('SIM', 'Sim'), ('NAO', 'Não')],
        widget=forms.RadioSelect
    )
    telefone = forms.CharField(label='Telefone', max_length=20, required=False)
    acompanhantes = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        comparecera = cleaned_data.get('comparecera')
        telefone = cleaned_data.get('telefone')
        acompanhantes_json = cleaned_data.get('acompanhantes')

        # Validação convidado principal
        if comparecera == 'SIM' and not telefone:
            self.add_error('telefone', 'Telefone é obrigatório se você for ao evento.')

        if nome:
            if not Convidado.objects.filter(nome__iexact=nome.strip()).exists():
                self.add_error('nome', 'Seu nome não está na lista de convidados.')

        # Validação acompanhantes
        acompanhantes_list = []
        if acompanhantes_json:
            try:
                acompanhantes_list = json.loads(acompanhantes_json)
            except json.JSONDecodeError:
                self.add_error('acompanhantes', 'Dados dos acompanhantes inválidos.')
                return cleaned_data

            if not isinstance(acompanhantes_list, list):
                self.add_error('acompanhantes', 'Formato dos acompanhantes inválido.')
                return cleaned_data

            for idx, acomp in enumerate(acompanhantes_list):
                nome_acomp = acomp.get('nome', '').strip()
                telefone_acomp = acomp.get('telefone', '').strip()

                if not nome_acomp:
                    self.add_error('acompanhantes', f'O nome do acompanhante #{idx+1} é obrigatório.')

                if not telefone_acomp:
                    self.add_error('acompanhantes', f'O telefone do acompanhante #{idx+1} é obrigatório.')

                # Verifica se acompanhante está na lista
                if nome_acomp and not Convidado.objects.filter(nome__iexact=nome_acomp).exists():
                    self.add_error('acompanhantes', f'O acompanhante "{nome_acomp}" não está na lista de convidados.')

        return cleaned_data