(function () {
  const estantes = document.getElementById("lista-estantes");
  const novedades = document.getElementById("lista-novedades");

  const iconos = {
    programacion: "code-xml",
    ingenieria: "cog",
    matematicas: "sigma",
    ciencias: "atom",
    literatura: "feather",
    economia: "trending-up",
    historia: "landmark"
  };

  function pintarEstantes(categorias) {
    estantes.innerHTML = categorias
      .map(
        (c) => `<a class="estante" href="catalogo.html?categoria=${encodeURIComponent(c.slug)}">
          <div class="estante__cabecera">
            <i data-lucide="${iconos[c.slug] || "book"}" class="icono--grande"></i>
            <i data-lucide="arrow-up-right" class="icono--chico"></i>
          </div>
          <div>
            <p class="estante__nombre">${Util.escapar(c.nombre)}</p>
            <p class="estante__conteo">${c.total_libros} títulos</p>
          </div>
        </a>`
      )
      .join("");
  }

  async function cargar() {
    try {
      const [categorias, libros] = await Promise.all([
        Api.get("/categorias/"),
        Api.get("/libros/", { ordering: "-año", disponible: true, tamano: 8 })
      ]);
      pintarEstantes(categorias);
      novedades.innerHTML = libros.results.map(Util.fichaLibro).join("");
      UI.refrescarIconos();
    } catch (e) {
      UI.aviso(e.message, "error");
    }
  }

  cargar();
})();