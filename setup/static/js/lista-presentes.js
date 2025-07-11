window.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.card').forEach(card => {
      const title = card.querySelector('.card-title');

      // Verifica se o título tem mais de duas linhas
      const lineHeight = parseFloat(getComputedStyle(title).lineHeight);
      const lines = title.scrollHeight / lineHeight;

      if (lines > 2) {
        card.classList.add('expandable');
      }
    });
  });


  //FILTRO SUBCATEGORIAS

    //LUA DE MEL

  let filtroOrdenarLua = null;
  let filtroSubcategoriaLua = "Todas";

  function atualizarProdutosLua() {
    const url = `/ajax/filtrar-lua-de-mel/?subcategoria=${filtroSubcategoriaLua}&ordenar=${filtroOrdenarLua || ''}`;

    fetch(url)
      .then(response => {
        if (!response.ok) throw new Error("Erro ao buscar produtos filtrados.");
        return response.text();
      })
      .then(html => {
        document.getElementById('product-grid-lua').innerHTML = html;
      })
      .catch(error => {
        console.error(error);
        alert("Erro ao carregar produtos.");
      });
  }

  // Botões de ordenação
  document.querySelectorAll('.btn-ordenar-lua').forEach(button => {
    button.addEventListener('click', function () {
      filtroOrdenarLua = this.getAttribute('data-ordenar');
      atualizarProdutosLua();
    });
  });

  // Filtros por subcategoria
  document.querySelectorAll('.filtro-subcategoria-lua').forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      filtroSubcategoriaLua = this.getAttribute('data-subcategoria');
      atualizarProdutosLua();
    });
  });



    //CASA

  let filtroOrdenarCasa = null;
  let filtroSubcategoriaCasa = "Todas";

  function atualizarProdutosCasa() {
    const url = `/ajax/filtrar-nosso-lar/?subcategoria=${filtroSubcategoriaCasa}&ordenar=${filtroOrdenarCasa || ''}`;

    fetch(url)
      .then(response => {
        if (!response.ok) throw new Error("Erro ao buscar produtos filtrados.");
        return response.text();
      })
      .then(html => {
        document.getElementById('product-grid-casa').innerHTML = html;
      })
      .catch(error => {
        console.error(error);
        alert("Erro ao carregar produtos.");
      });
  }

  // Botões de ordenação
  document.querySelectorAll('.btn-ordenar-casa').forEach(button => {
    button.addEventListener('click', function () {
      filtroOrdenarCasa = this.getAttribute('data-ordenar');
      atualizarProdutosCasa();
    });
  });

  // Filtros por subcategoria
  document.querySelectorAll('.filtro-subcategoria-casa').forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      filtroSubcategoriaCasa = this.getAttribute('data-subcategoria');
      atualizarProdutosCasa();
    });
  });