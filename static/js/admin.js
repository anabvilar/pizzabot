const statusOpcoes = ["recebido", "em preparo", "saiu para entrega", "entregue", "cancelado"]; 
async function carregarPedidos() {
const response = await fetch("/admin/pedidos");
const pedidos = await response.json();
renderizarResumo(pedidos);
renderizarTabela(pedidos);
} 

function renderizarResumo(pedidos) {
		const total = pedidos.length;
		const recebidos = pedidos.filter(p => p.status === "recebido").length;
		const emPreparo = pedidos.filter(p => p.status === "em preparo").length;
		const entregues = pedidos.filter(p => p.status === "entregue").length;
		
		document.getElementById("resumo").innerHTML = `
		    <div class="card"><h3>${total}</h3><p>Total de Pedidos</p></div>
		    <div class="card"><h3>${recebidos}</h3><p>Recebidos</p></div>
		    <div class="card"><h3>${emPreparo}</h3><p>Em Preparo</p></div>
		    <div class="card"><h3>${entregues}</h3><p>Entregues</p></div>
`;
}

function renderizarTabela(pedidos) {
		const corpo = document.getElementById("corpoPedidos");
		if (pedidos.length === 0) {
		corpo.innerHTML = <tr><td colspan="11" style="text-align:center; color:#999; padding:30px;">Nenhum pedido recebido hoje.</td></tr>;
		return;
}

		corpo.innerHTML = pedidos.map(p => `
		    <tr>
		        <td>#${p.id}</td>
		        <td>${p.nome_cliente}</td>
		        <td>${p.telefone}</td>
		        <td>${p.endereco}</td>
		        <td>${p.tamanho}</td>
		        <td>${p.sabor}</td>
		        <td>${p.borda}</td>
		        <td>${p.observacoes || "—"}</td>
		        <td><span class="badge ${badgeClasse(p.status)}">${p.status}</span></td>
		        <td>${p.criado_em}</td>
		        <td>
		            <select onchange="atualizarStatus(${p.id}, this.value)">
		                ${statusOpcoes.map(s => `<option value="${s}" ${s === p.status ? "selected" : ""}>${s}</option>`).join("")}
		            </select>
		        </td>
		    </tr>
		`).join("");
}

function badgeClasse(status) {
		const mapa = { "recebido": "recebido", "em preparo": "em-preparo", "saiu para entrega": "saiu", "entregue": "entregue", "cancelado": "cancelado" };
		return mapa[status] || "recebido";
}

async function atualizarStatus(id, novoStatus) {
		const response = await fetch(/admin/pedidos/${id}/status, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ status: novoStatus })
		});
		const dados = await response.json();
		if (dados.mensagem) { carregarPedidos(); } else { alert("Erro ao atualizar status do pedido."); }
}

document.getElementById("btnAtualizar").addEventListener("click", carregarPedidos);
setInterval(carregarPedidos, 15000); // Atualização automática a cada 15 segundos
carregarPedidos();