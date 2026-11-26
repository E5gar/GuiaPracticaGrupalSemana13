const API = "http://127.0.0.1:8001/api";
const CLAVE_TOKEN = "tecnomarket-token";

const token = () => localStorage.getItem(CLAVE_TOKEN);
const soles = (valor) => "S/ " + Number(valor).toFixed(2);
const esc = (texto) => String(texto ?? "").replace(/[&<>"']/g, (c) => "&#" + c.charCodeAt(0) + ";");

function mensajeError(datos, estado) {
  if (estado === 429) return "Demasiadas peticiones, intenta mas tarde";
  if (!datos) return "Error " + estado;
  return Object.values(datos).flat().join(" ");
}

async function pedir(ruta, metodo = "GET", cuerpo) {
  const cabeceras = { "Content-Type": "application/json" };
  if (token()) cabeceras.Authorization = "Token " + token();
  const respuesta = await fetch(API + ruta, {
    method: metodo,
    headers: cabeceras,
    body: cuerpo ? JSON.stringify(cuerpo) : undefined,
  }).catch(() => {
    throw new Error("No se pudo conectar con la API");
  });
  const datos = respuesta.status === 204 ? null : await respuesta.json().catch(() => null);
  if (respuesta.status === 401) {
    localStorage.removeItem(CLAVE_TOKEN);
    location.href = "login.html";
  }
  if (!respuesta.ok) throw new Error(mensajeError(datos, respuesta.status));
  return datos;
}

const fallo = (error) => UI.aviso(error.message, "error");

function exigirSesion() {
  if (!token()) location.href = "login.html";
  return Boolean(token());
}

function tarjeta(p) {
  const imagen = p.imagenes.length ? p.imagenes[0].url : "https://picsum.photos/seed/" + p.id + "/600/600";
  const anterior = p.descuento > 0 ? "<s>" + soles(p.precio) + "</s>" : "";
  const estado = p.disponible
    ? '<span class="etiqueta etiqueta--ok">Stock ' + p.stock + "</span>"
    : '<span class="etiqueta etiqueta--error">Agotado</span>';
  return `<a class="tarjeta" href="producto.html?id=${p.id}">
    <div class="tarjeta__media tarjeta__media--cuadrada"><img src="${esc(imagen)}" alt="Lorem ipsum dolor" loading="lazy"></div>
    <div class="tarjeta__cuerpo">
      <span class="tarjeta__meta">${esc(p.marca)} | ${esc(p.categoria.nombre)}</span>
      <h4 class="tarjeta__titulo">${esc(p.nombre)}</h4>
      <p class="tarjeta__precio">${anterior}${soles(p.precio_con_descuento)}</p>
      <div class="tarjeta__pie fila fila--entre">${estado}<span class="tarjeta__meta">${p.rating_promedio} / 5</span></div>
    </div>
  </a>`;
}

function pintarCabecera() {
  const actual = location.pathname.split("/").pop() || "index.html";
  const enlace = (archivo, texto) =>
    `<a href="${archivo}"${archivo === actual ? ' aria-current="page"' : ""}>${texto}</a>`;
  document.getElementById("cabecera").innerHTML = `<div class="contenedor cabecera__fila">
    <a class="marca" href="index.html"><img class="marca__logo" src="../../compartido/img/icon-fis.png" alt="Lorem ipsum dolor">TecnoMarket</a>
    <nav class="cabecera__nav" id="nav">${enlace("index.html", "Inicio")}${enlace("catalogo.html", "Catalogo")}${enlace("carrito.html", "Carrito")}${enlace("ordenes.html", "Ordenes")}</nav>
    <div class="cabecera__acciones">
      <button class="boton-icono" type="button" data-tema-toggle><i data-lucide="sun" class="icono-sol"></i><i data-lucide="moon" class="icono-luna"></i></button>
      <a class="boton-icono" href="carrito.html" aria-label="Carrito"><i data-lucide="shopping-cart"></i></a>
      <a class="boton-icono" href="login.html" id="sesion" aria-label="${token() ? "Cerrar sesion" : "Ingresar"}"><i data-lucide="${token() ? "log-out" : "user"}"></i></a>
      <button class="boton-icono menu-boton" type="button" data-menu-toggle aria-controls="nav" aria-expanded="false" aria-label="Menu"><i data-lucide="menu"></i></button>
    </div>
  </div>`;
  document.getElementById("sesion").addEventListener("click", () => {
    if (token()) localStorage.removeItem(CLAVE_TOKEN);
  });
  UI.refrescarIconos();
}

pintarCabecera();
