const zonaProductos = document.getElementById("productos");
const zonaDestacados = document.getElementById("destacados");
const formularioFiltros = document.getElementById("filtros");
let pagina = 1;

async function cargarCatalogo() {
  const parametros = new URLSearchParams();
  new FormData(formularioFiltros).forEach((valor, clave) => {
    if (valor) parametros.set(clave, valor);
  });
  parametros.set("page", pagina);
  const datos = await pedir("/productos/?" + parametros);
  document.getElementById("total").textContent = datos.count + " productos";
  zonaProductos.innerHTML = datos.results.length
    ? datos.results.map(tarjeta).join("")
    : '<div class="vacio tm-ancho">No hay productos con esos filtros</div>';
  const paginas = Math.ceil(datos.count / 24);
  document.getElementById("paginacion").innerHTML = Array.from(
    { length: paginas },
    (_, i) => `<button class="paginacion__item" data-pagina="${i + 1}"${i + 1 === pagina ? ' aria-current="page"' : ""}>${i + 1}</button>`
  ).join("");
}

async function cargarInicio() {
  const datos = await pedir("/productos/");
  zonaDestacados.innerHTML = datos.results.slice(0, 8).map(tarjeta).join("");
  const iconos = { Laptops: "laptop", Smartphones: "smartphone", Componentes: "cpu", Accesorios: "headphones" };
  document.getElementById("categorias").innerHTML = Object.entries(iconos)
    .map(([nombre, icono]) => `<a class="dato" href="catalogo.html?categoria=${nombre}"><i data-lucide="${icono}" class="icono--grande"></i><span class="dato__nombre">${nombre}</span></a>`)
    .join("");
  UI.refrescarIconos();
}

if (formularioFiltros) {
  const inicial = new URLSearchParams(location.search).get("categoria");
  if (inicial) formularioFiltros.elements.categoria.value = inicial;
  formularioFiltros.addEventListener("submit", (e) => {
    e.preventDefault();
    pagina = 1;
    cargarCatalogo().catch(fallo);
  });
  formularioFiltros.addEventListener("reset", () => {
    setTimeout(() => {
      formularioFiltros.elements.categoria.value = "";
      pagina = 1;
      cargarCatalogo().catch(fallo);
    });
  });
  document.getElementById("paginacion").addEventListener("click", (e) => {
    const boton = e.target.closest("[data-pagina]");
    if (!boton) return;
    pagina = Number(boton.dataset.pagina);
    cargarCatalogo().then(() => scrollTo(0, 0)).catch(fallo);
  });
  cargarCatalogo().catch(fallo);
}

if (zonaDestacados) cargarInicio().catch(fallo);
