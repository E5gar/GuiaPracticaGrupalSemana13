(function () {
  const TAMANO = 20;
  const estado = { page: 1, search: "", categoria: "", desde: "", disponible: false, orden: "título" };

  const rejilla = document.getElementById("rejilla-libros");
  const vacio = document.getElementById("vacio-libros");
  const cuenta = document.getElementById("cuenta-resultados");
  const paginacion = document.getElementById("paginacion");
  const formulario = document.getElementById("filtros");
  const campoBusqueda = document.getElementById("f-busqueda");
  const campoCategoria = document.getElementById("f-categoria");
  const campoAnio = document.getElementById("f-anio");
  const campoOrden = document.getElementById("f-orden");
  const campoDisponible = document.getElementById("f-disponible");
  const detalle = document.getElementById("detalle-contenido");

  function esqueletos() {
    return Array.from({ length: 8 }, () =>
      '<div class="tarjeta"><div class="tarjeta__media esqueleto"></div><div class="tarjeta__cuerpo"><div class="esqueleto fila-esqueleto"></div></div></div>'
    ).join("");
  }

  function pintarPaginacion(total) {
    const paginas = Math.max(1, Math.ceil(total / TAMANO));
    if (paginas === 1) {
      paginacion.innerHTML = "";
      return;
    }
    paginacion.innerHTML = `
      <button class="paginacion__item" type="button" data-ir="${estado.page - 1}" ${estado.page === 1 ? "disabled" : ""} aria-label="Página anterior"><i data-lucide="chevron-left" class="icono--chico"></i></button>
      <span class="paginacion__item" aria-current="page">${estado.page}</span>
      <span class="texto-pequeno texto-apagado">de ${paginas}</span>
      <button class="paginacion__item" type="button" data-ir="${estado.page + 1}" ${estado.page >= paginas ? "disabled" : ""} aria-label="Página siguiente"><i data-lucide="chevron-right" class="icono--chico"></i></button>`;
  }

  async function cargar() {
    rejilla.innerHTML = esqueletos();
    vacio.classList.add("oculto");
    try {
      const datos = await Api.get("/libros/", {
        page: estado.page,
        search: estado.search,
        categoria: estado.categoria,
        "año__gte": estado.desde,
        disponible: estado.disponible,
        ordering: estado.orden
      });
      cuenta.textContent = datos.count + (datos.count === 1 ? " título" : " títulos");
      rejilla.innerHTML = datos.results.map(Util.fichaLibro).join("");
      vacio.classList.toggle("oculto", datos.results.length > 0);
      pintarPaginacion(datos.count);
      UI.refrescarIconos();
    } catch (e) {
      rejilla.innerHTML = "";
      paginacion.innerHTML = "";
      vacio.classList.remove("oculto");
      UI.aviso(e.message, "error");
    }
  }

  async function cargarCategorias() {
    try {
      const categorias = await Api.get("/categorias/");
      campoCategoria.innerHTML =
        '<option value="">Todas</option>' +
        categorias.map((c) => `<option value="${Util.escapar(c.slug)}">${Util.escapar(c.nombre)} (${c.total_libros})</option>`).join("");
      campoCategoria.value = estado.categoria;
    } catch (e) {
      UI.aviso(e.message, "error");
    }
  }

  async function abrirDetalle(id) {
    try {
      const l = await Api.get("/libros/" + id + "/");
      const personal = Sesion.esPersonal();
      const accion = personal
        ? `<a class="boton boton--solido" href="prestamos.html?libro=${l.id}"><i data-lucide="hand-coins" class="icono--chico"></i>Registrar préstamo</a>`
        : `<div class="alerta-caja"><i data-lucide="id-card" class="icono"></i><span>Para llevarlo a casa, presenta tu carnet vigente en el mostrador de la biblioteca.</span></div>`;
      detalle.innerHTML = `<div class="detalle">
        <div class="detalle__portada"><img src="${Util.escapar(l.portada)}" alt="Lorem ipsum dolor"></div>
        <div class="pila">
          <span class="etiqueta ${l.disponible ? "etiqueta--ok" : "etiqueta--error"}">${l.disponible ? l.stock + " disponibles" : "Agotado"}</span>
          <h3 id="detalle-titulo">${Util.escapar(l.titulo)}</h3>
          <p class="texto-apagado">${Util.escapar(l.autor.nombre)} · ${Util.escapar(l.autor.nacionalidad)}</p>
          <dl class="detalle__datos">
            <dt>ISBN</dt><dd class="mono">${Util.escapar(l.isbn)}</dd>
            <dt>Editorial</dt><dd>${Util.escapar(l.editorial)}</dd>
            <dt>Año</dt><dd>${l.anio}</dd>
            <dt>Categoría</dt><dd>${Util.escapar(l.categoria_nombre)}</dd>
            <dt>Ubicación</dt><dd>${Util.escapar(l.ubicacion)}</dd>
          </dl>
          <p class="texto-pequeno texto-apagado">${Util.escapar(l.autor.biografia)}</p>
          ${accion}
        </div>
      </div>`;
      UI.abrirModal("modal-libro");
      UI.refrescarIconos();
    } catch (e) {
      UI.aviso(e.message, "error");
    }
  }

  const reiniciar = () => {
    estado.page = 1;
    cargar();
  };

  campoBusqueda.addEventListener(
    "input",
    Util.retraso(() => {
      estado.search = campoBusqueda.value.trim();
      reiniciar();
    })
  );
  campoCategoria.addEventListener("change", () => {
    estado.categoria = campoCategoria.value;
    reiniciar();
  });
  campoAnio.addEventListener("change", () => {
    estado.desde = campoAnio.value;
    reiniciar();
  });
  campoOrden.addEventListener("change", () => {
    estado.orden = campoOrden.value;
    reiniciar();
  });
  campoDisponible.addEventListener("change", () => {
    estado.disponible = campoDisponible.checked;
    reiniciar();
  });
  formulario.addEventListener("submit", (e) => e.preventDefault());
  formulario.addEventListener("reset", () => {
    setTimeout(() => {
      Object.assign(estado, { page: 1, search: "", categoria: "", desde: "", disponible: false, orden: "título" });
      cargar();
    }, 0);
  });

  paginacion.addEventListener("click", (e) => {
    const boton = e.target.closest("[data-ir]");
    if (!boton) return;
    estado.page = Number(boton.dataset.ir);
    cargar();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  document.addEventListener("click", (e) => {
    const enlace = e.target.closest("[data-ver]");
    if (!enlace) return;
    e.preventDefault();
    abrirDetalle(enlace.dataset.ver);
  });

  const url = new URLSearchParams(location.search);
  estado.search = url.get("search") || "";
  estado.categoria = url.get("categoria") || "";
  if (url.get("orden") === "reciente") {
    estado.orden = "-año";
    campoOrden.value = "-año";
  }
  campoBusqueda.value = estado.search;

  (async function iniciar() {
    await cargarCategorias();
    await cargar();
    const libroInicial = url.get("libro");
    if (libroInicial) abrirDetalle(libroInicial);
  })();
})();