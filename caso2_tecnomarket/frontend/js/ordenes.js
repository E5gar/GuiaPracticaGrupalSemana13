const zonaOrdenes = document.getElementById("ordenes");
const colores = { pendiente: "alerta", pagada: "info", enviada: "info", entregada: "ok", cancelada: "error" };

async function cargarOrdenes() {
  const datos = await pedir("/ordenes/mis-ordenes/?limit=20&ordering=-fecha_creacion");
  zonaOrdenes.innerHTML = datos.results.length
    ? datos.results
        .map((o) => `<article class="tm-bloque pila pila--chica">
          <div class="fila fila--entre"><h4>Orden ${o.id}</h4><span class="etiqueta etiqueta--${colores[o.estado]}">${o.estado}</span></div>
          <p class="texto-pequeno texto-apagado">${new Date(o.fecha_creacion).toLocaleDateString("es-PE")} | ${esc(o.metodo_pago)} | ${esc(o.direccion_envio)}</p>
          ${o.numero_seguimiento ? `<p class="mono">Seguimiento: ${esc(o.numero_seguimiento)}</p>` : ""}
          <div class="fila fila--entre">
            <strong>${soles(o.total)}</strong>
            ${o.estado === "pendiente" ? `<button class="boton boton--peligro boton--chico" type="button" data-cancelar="${o.id}">Cancelar</button>` : ""}
          </div>
        </article>`)
        .join("")
    : '<div class="vacio">Aun no tienes ordenes</div>';
}

zonaOrdenes.addEventListener("click", async (e) => {
  const boton = e.target.closest("[data-cancelar]");
  if (!boton) return;
  try {
    await pedir(`/ordenes/${boton.dataset.cancelar}/cancelar/`, "POST");
    UI.aviso("Orden cancelada", "ok");
    await cargarOrdenes();
  } catch (error) {
    fallo(error);
  }
});

if (exigirSesion()) cargarOrdenes().catch(fallo);
