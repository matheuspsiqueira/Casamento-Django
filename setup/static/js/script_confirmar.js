/*MENSAGEM*/

function mostrarMensagemFeedback(texto, tipo = 'sucesso', duracao = 4000) {
  const div = document.getElementById('mensagem-feedback');
  if (!div) return;

  div.textContent = texto;
  div.classList.remove('sucesso', 'error'); // remove só as classes de estado
  div.classList.add(tipo); // adiciona a classe correta

  div.style.display = 'block';
  div.style.opacity = '1';

  setTimeout(() => {
    div.style.opacity = '0';
    setTimeout(() => {
      div.style.display = 'none';
      div.textContent = '';
    }, 300);
  }, duracao);
}

/* Contador acompanhantes */

let adultosCount = 0;
let criancasCount = 0;

function updateCount(type, change) {
  if (type === 'adultos') {
    adultosCount = Math.max(0, adultosCount + change);
    document.getElementById('adultos').textContent = adultosCount;
    renderAcompanhantes();
  } else if (type === 'criancas') {
    criancasCount = Math.max(0, criancasCount + change);
    document.getElementById('criancas').textContent = criancasCount;
  }
}

/* Renderiza inputs de acompanhantes adultos */
function renderAcompanhantes() {
  const container = document.getElementById('acompanhantes-container');
  container.innerHTML = '';

  for (let i = 1; i <= adultosCount; i++) {
    const nome = document.createElement('input');
    nome.type = 'text';
    nome.name = `acompanhante_nome_${i}`;
    nome.id = `acompanhante_nome_${i}`;
    nome.placeholder = `Nome completo acompanhante ${i} *`;
    nome.required = true;

    const telefone = document.createElement('input');
    telefone.type = 'tel';
    telefone.name = `acompanhante_tel_${i}`;
    telefone.id = `acompanhante_tel_${i}`;
    telefone.placeholder = `Telefone acompanhante ${i} *`;
    telefone.required = true;
    telefone.classList.add('telefone');

    const pair = document.createElement('div');
    pair.classList.add('acompanhante-pair');
    pair.appendChild(nome);
    pair.appendChild(telefone);

    container.appendChild(pair);
  }

  $('.telefone').mask('(00) 00000-0000');
}

const form = document.querySelector('form');

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

form.addEventListener('submit', async function (e) {
  e.preventDefault();

  const acompanhantes = [];
  const total = document.querySelectorAll('.acompanhante-pair').length;

  for (let i = 1; i <= total; i++) {
    const nome = document.querySelector(`#acompanhante_nome_${i}`)?.value.trim();
    const tel = document.querySelector(`#acompanhante_tel_${i}`)?.value.trim();
    if (nome && tel) {
      acompanhantes.push({ nome: nome, telefone: tel });
    } else {
      mostrarMensagemFeedback(`Por favor, preencha nome e telefone do acompanhante ${i}.`, 'error');
      return; // bloqueia envio se algum campo estiver vazio
    }
  }

  document.getElementById('acompanhantes').value = JSON.stringify(acompanhantes);

  const formData = new FormData(form);

  try {
    const response = await fetch(form.action, {
      method: "POST",
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrftoken
      }
    });

    let data;
    const clone = response.clone();

    try {
      data = await response.json();
    } catch (jsonError) {
      const texto = await clone.text();
      console.error("Resposta não é JSON. Conteúdo bruto:", texto);
      mostrarMensagemFeedback("Erro inesperado do servidor.", 'error');
      return;
    }

    if (data.status === 'sucesso') {
      mostrarMensagemFeedback(data.mensagem, 'sucesso');
      form.reset();
      document.getElementById('acompanhantes-container').innerHTML = '';
      adultosCount = 0;
      criancasCount = 0;
      document.getElementById('adultos').textContent = '0';
      document.getElementById('criancas').textContent = '0';
    } else {
      mostrarMensagemFeedback(data.mensagem || "Erro no envio do formulário.", 'error');
    }
  } catch (err) {
    console.error("Erro na requisição:", err);
    mostrarMensagemFeedback("Erro ao enviar dados para o servidor.", 'error');
  }
});

console.log('CSRF Token:', csrftoken);
