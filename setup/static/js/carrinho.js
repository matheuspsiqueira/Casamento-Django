function irParaEtapa(numero) {
  // Oculta todos os conteúdos de etapa
  document.querySelectorAll('.etapa-conteudo').forEach(el => el.style.display = 'none');

  // Remove classe ativa de todas as abas
  document.querySelectorAll('.etapa-tab').forEach(tab => tab.classList.remove('ativa'));

  // Exibe a etapa correspondente
  document.getElementById('etapa-' + numero).style.display = 'block';

  // Marca a etapa atual como ativa
  document.querySelector('.etapa-tab[data-etapa="' + numero + '"]').classList.add('ativa');
}


// Adiciona o evento de clique nas etapas
document.addEventListener("DOMContentLoaded", function () {
  // Mostra a Etapa 1 ao iniciar
  irParaEtapa(1);

  // Associa clique a cada aba de etapa
  document.querySelectorAll('.etapa-tab').forEach(function(tab) {
    tab.addEventListener('click', function() {
      const numeroEtapa = this.getAttribute('data-etapa');
      irParaEtapa(numeroEtapa);
    });
  });
});


$(document).ready(function () {
  console.log("jQuery está funcionando!");
  $('input[name="telefone"]').mask('(00) 00000-0000');
});