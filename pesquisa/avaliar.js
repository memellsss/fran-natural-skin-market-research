"use strict";

const form = document.querySelector("#avaliacao");
const status = document.querySelector("#estado");
const random = crypto.getRandomValues(new Uint8Array(1))[0];
const variante = random % 2 === 0 ? "A" : "B";

const cenarios = {
  A: "Imagine a página com uma lista de 20 códigos de tonalidade e a descrição da base acima.",
  B: "Imagine a mesma página, com os mesmos 20 códigos e um guia que usa fotos sob iluminação padronizada, indica o subtom e sugere referências aproximadas de outras marcas.",
};

document.querySelector("#cenario").textContent = cenarios[variante];
form.hidden = false;
form.addEventListener("submit", (event) => {
  event.preventDefault();
  const values = Object.fromEntries(new FormData(form));
  if (values.elegivel !== "sim") {
    status.textContent = "Agradecemos o interesse. O piloto não exporta respostas fora do público definido.";
    return;
  }

  const result = {
    versao_questionario: 1,
    variante,
    experiencia: values.experiencia,
    confianca: Number(values.confianca),
    escolheria_tom: values.escolheria_tom,
    intencao_compra: Number(values.intencao_compra),
    barreira: values.barreira,
    melhoria: values.melhoria,
    sem_estoque: values.sem_estoque,
  };
  const file = new Blob([JSON.stringify(result, null, 2) + "\n"], { type: "application/json" });
  const url = URL.createObjectURL(file);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "resposta-fran-natural-skin.json";
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  status.textContent = "O arquivo foi gerado no seu dispositivo. Não enviamos a resposta.";
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
});
