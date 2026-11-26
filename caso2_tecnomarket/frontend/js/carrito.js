const zonaItems = document.getElementById("items");
const formularioPago = document.getElementById("form-pago");

function pintarCarrito(c) {
  zonaItems.innerHTML = c.items.length
    ? `<div class="tabla-envoltura"><table class="tabla">
        <thead><tr><th>Producto</th><th>Precio</th><th>Cantidad</th><th class="num">Importe</th><th></th></tr></thead>
        <tbody>${c.items
          .map((i) => `<tr>
            <td><a href="producto.html?id=${i.producto}">${esc(i.nombre)}</a></td>
            <td>${soles(i.precio_unitario)}</td>
            <td><input class="campo__control tm-cantidad" type="number" min="1" value="${i.cantidad}" data-cantidad="${i.producto}" aria-label="Cantidad"></td>
            <td class="num">${soles(i.importe)}</td>
            <td><button class="boton-icono" type="button" data-eliminar="${i.producto}" aria-label="Eliminar"><i data-lucide="trash-2"></i></button></td>
          </tr>`)
          .join("")}</tbody></table></div>`
    : '<div class="vacio">Tu carrito esta vacio<a class="boton" href="catalogo.html">Ver catalogo</a></div>';
  const fila = (nombre, valor) => `<div class="fila fila--entre"><span>${nombre}</span><span>${valor}</span></div>`;
  document.getElementById("resumen").innerHTML =
    fila("Subtotal", soles(c.subtotal)) +
    fila("IGV", soles(c.impuestos)) +
    fila("Total", soles(c.total)) +
    fila("Cupon", esc(c.cupon) || "Ninguno") +
    `<span class="dato__nombre">A pagar</span><span class="dato__valor">${soles(c.total_con_descuento)}</span>`;
  formularioPago.querySelectorAll("button").forEach((b) => (b.disabled = !c.items.length));
  UI.refrescarIconos();
}

const cargarCarrito = () => pedir("/carrito/").then(pintarCarrito).catch(fallo);

function cambiar(accion, cuerpo) {
  return pedir(`/carrito/${accion}/`, "POST", cuerpo)
    .then(pintarCarrito)
    .catch((error) => {
      fallo(error);
      cargarCarrito();
    });
}

zonaItems.addEventListener("change", (e) => {
  const id = e.target.dataset.cantidad;
  if (id) cambiar("actualizar", { producto_id: Number(id), cantidad: Number(e.target.value) });
});

zonaItems.addEventListener("click", (e) => {
  const boton = e.target.closest("[data-eliminar]");
  if (boton) cambiar("eliminar", { producto_id: Number(boton.dataset.eliminar) });
});

document.getElementById("vaciar").addEventListener("click", () => cambiar("vaciar"));

formularioPago.addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    const orden = await pedir("/carrito/checkout/", "POST", Object.fromEntries(new FormData(formularioPago)));
    UI.aviso("Orden " + orden.id + " creada", "ok");
    setTimeout(() => (location.href = "ordenes.html"), 1200);
  } catch (error) {
    fallo(error);
  }
});

if (exigirSesion()) cargarCarrito();
