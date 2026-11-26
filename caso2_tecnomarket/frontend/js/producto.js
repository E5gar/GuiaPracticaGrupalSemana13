const idProducto = Number(new URLSearchParams(location.search).get("id")) || 1;

async function cargarDetalle() {
  const p = await pedir(`/productos/${idProducto}/`);
  const fotos = p.imagenes.map((i) => i.url);
  const principal = fotos[0] || `https://picsum.photos/seed/${p.id}/600/600`;
  document.getElementById("detalle").innerHTML = `<div class="tm-detalle">
    <div class="pila">
      <img class="tm-foto" id="foto" src="${esc(principal)}" alt="Lorem ipsum dolor">
      <div class="fila tm-miniaturas">${fotos.map((u) => `<img src="${esc(u)}" alt="Lorem ipsum dolor">`).join("")}</div>
    </div>
    <div class="pila">
      <span class="texto-apagado">${esc(p.marca)} | ${esc(p.categoria.nombre)} | ${esc(p.sku)}</span>
      <h2>${esc(p.nombre)}</h2>
      <p>${esc(p.descripcion)}</p>
      <h3>${soles(p.precio_con_descuento)}</h3>
      <div class="fila">
        ${p.descuento > 0 ? `<span class="etiqueta etiqueta--acento">${p.descuento}% de descuento</span>` : ""}
        <span class="etiqueta ${p.disponible ? "etiqueta--ok" : "etiqueta--error"}">Stock ${p.stock}</span>
        <span class="etiqueta">${p.rating_promedio} / 5</span>
      </div>
      <div class="tabla-envoltura"><table class="tabla"><tbody>${Object.entries(p.especificaciones || {})
        .map(([k, v]) => `<tr><td>${esc(k.replace(/_/g, " "))}</td><td>${esc(v)}</td></tr>`)
        .join("")}</tbody></table></div>
      <form class="pila" id="form-agregar">
        <label class="campo"><span class="campo__etiqueta">Cantidad</span><input class="campo__control" name="cantidad" type="number" min="1" value="1" required></label>
        <label class="campo"><span class="campo__etiqueta">Cupon</span><input class="campo__control" name="cupon" placeholder="CYBER20"></label>
        <button class="boton boton--solido" type="submit"${p.disponible ? "" : " disabled"}><i data-lucide="shopping-cart"></i>Agregar al carrito</button>
      </form>
    </div>
  </div>`;
  document.querySelectorAll(".tm-miniaturas img").forEach((mini) =>
    mini.addEventListener("click", () => (document.getElementById("foto").src = mini.src))
  );
  document.getElementById("form-agregar").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!exigirSesion()) return;
    const datos = new FormData(e.target);
    try {
      await pedir("/carrito/agregar/", "POST", {
        producto_id: p.id,
        cantidad: Number(datos.get("cantidad")),
        cupon: datos.get("cupon"),
      });
      UI.aviso("Producto agregado al carrito", "ok");
    } catch (error) {
      fallo(error);
    }
  });
  UI.refrescarIconos();
}

async function cargarResenas() {
  const datos = await pedir(`/productos/${idProducto}/rese%C3%B1as/`);
  const lista = datos.results || datos;
  document.getElementById("resenas").innerHTML = lista.length
    ? lista
        .map((r) => `<article class="tm-bloque pila pila--chica">
          <div class="fila fila--entre"><strong>${esc(r.titulo)}</strong><span class="etiqueta">${r.calificacion} / 5</span></div>
          <p>${esc(r.comentario)}</p>
          <div class="fila"><span class="texto-pequeno texto-apagado">${esc(r.usuario)}</span>${r.es_compra_verificada ? '<span class="etiqueta etiqueta--ok">Compra verificada</span>' : ""}</div>
        </article>`)
        .join("")
    : '<div class="vacio">Aun no hay opiniones</div>';
}

document.getElementById("form-resena").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!exigirSesion()) return;
  const cuerpo = Object.fromEntries(new FormData(e.target));
  try {
    await pedir("/rese%C3%B1as/", "POST", { ...cuerpo, producto: idProducto, calificacion: Number(cuerpo.calificacion) });
    e.target.reset();
    UI.aviso("Opinion publicada", "ok");
    await cargarResenas();
  } catch (error) {
    fallo(error);
  }
});

cargarDetalle().catch(fallo);
cargarResenas().catch(fallo);
