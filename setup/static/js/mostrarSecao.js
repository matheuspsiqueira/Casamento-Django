function mostrarSecao(id) {
  const secoes = document.querySelectorAll('.secao-detalhe');
  secoes.forEach(secao => secao.style.display = 'none');

  const secaoAlvo = document.getElementById(id);
  if (secaoAlvo) {
    secaoAlvo.style.display = 'block';
    secaoAlvo.scrollIntoView({ behavior: 'smooth' });
  }
}
