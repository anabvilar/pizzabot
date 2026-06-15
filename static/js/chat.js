const chatBox = document.getElementById("chatBox");
const inputMensagem = document.getElementById("inputMensagem");
const btnEnviar = document.getElementById("btnEnviar");

window.addEventListener("load", () => {
adicionarMensagem("Olá! Seja bem-vindo à Pizza Bot! Estou aqui para anotar seu pedido. Pode começar me dizendo seu nome!", "bot");
});

function adicionarMensagem(texto, tipo) {
const div = document.createElement("div");
div.classList.add("mensagem", tipo);
div.textContent = texto;
chatBox.appendChild(div);
chatBox.scrollTop = chatBox.scrollHeight;
}

function mostrarDigitando() {
const div = document.createElement("div");
div.classList.add("digitando");
div.id = "digitando";
div.textContent = "Pizza Bot está digitando...";
chatBox.appendChild(div);
chatBox.scrollTop = chatBox.scrollHeight;
}

function removerDigitando() {
const div = document.getElementById("digitando");
if (div) div.remove();
}

async function enviarMensagem() {
const texto = inputMensagem.value.trim();
if (!texto) return; 

adicionarMensagem(texto, "usuario");
inputMensagem.value = "";
btnEnviar.disabled = true;
mostrarDigitando();

try {
    const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensagem: texto })
    });

    const dados = await response.json();
    removerDigitando();

    if (dados.pedido_finalizado) {
        adicionarMensagem(dados.resposta, "sistema");
    } else {
        adicionarMensagem(dados.resposta, "bot");
    }

	} catch (erro) {
	    removerDigitando();
	    adicionarMensagem("Ops! Ocorreu um erro técnico. Tente novamente.", "bot");
	    console.error(erro);
	}

	btnEnviar.disabled = false;
	inputMensagem.focus();
} 
btnEnviar.addEventListener("click", enviarMensagem);
inputMensagem.addEventListener("keypress", (e) => { if (e.key === "Enter") enviarMensagem(); });