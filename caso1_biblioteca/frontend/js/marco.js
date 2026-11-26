(function () {
  const pagina = document.body.dataset.pagina || "";
  const sesion = Sesion.activa();
  const usuario = Sesion.usuario();

  const enlaces = [
    ["index.html", "Inicio", "inicio"],
    ["catalogo.html", "Catálogo", "catalogo"]
  ];
  if (sesion) {
    enlaces.push(["prestamos.html", Sesion.esPersonal() ? "Préstamos" : "Mis préstamos", "prestamos"]);
    enlaces.push(["perfil.html", "Mi cuenta", "perfil"]);
  } else {
    enlaces.push(["login.html", "Ingresar", "login"]);
  }

  const nav = enlaces
    .map(([href, texto, clave]) => `<a href="${href}"${pagina === clave ? ' aria-current="page"' : ""}>${texto}</a>`)
    .join("");
  const salir = sesion ? '<a href="#" data-salir>Salir</a>' : "";

  const anuncio = document.getElementById("marco-anuncio");
  if (anuncio) {
    const items = [
      ["clock", "Préstamo a domicilio hasta 14 días"],
      ["receipt", "Multa de S/ 2.00 por día de atraso"],
      ["library", "Máximo 5 préstamos activos por usuario"],
      ["id-card", "Presenta tu carnet vigente en el mostrador"]
    ];
    anuncio.outerHTML = `<div class="anuncio"><div class="anuncio__pista">${items
      .map(([icono, texto]) => `<span class="anuncio__item"><i data-lucide="${icono}" class="icono--chico"></i>${texto}</span>`)
      .join("")}</div></div>`;
  }

  const cabecera = document.getElementById("marco-cabecera");
  if (cabecera) {
    cabecera.outerHTML = `<header class="cabecera">
      <div class="contenedor cabecera__fila">
        <a class="marca" href="index.html">
          <img class="marca__logo" src="../../compartido/img/icon-uncp.png" alt="Lorem ipsum dolor">
          <span class="marca__separador"></span>
          <img class="marca__logo" src="../../compartido/img/icon-fis.png" alt="Lorem ipsum dolor">
        </a>
        <nav class="cabecera__nav" id="nav-principal">${nav}${salir}</nav>
        <div class="cabecera__acciones">
          <button class="boton-icono" type="button" data-tema-toggle>
            <i data-lucide="sun" class="icono-sol"></i>
            <i data-lucide="moon" class="icono-luna"></i>
          </button>
          <button class="boton-icono menu-boton" type="button" data-menu-toggle aria-controls="nav-principal" aria-expanded="false" aria-label="Menú">
            <i data-lucide="menu"></i>
          </button>
        </div>
      </div>
    </header>`;
  }

  const pie = document.getElementById("marco-pie");
  if (pie) {
    pie.outerHTML = `<footer class="pie">
      <div class="contenedor pie__rejilla">
        <div>
          <p class="pie__titulo">Biblioteca Central</p>
          <p class="texto-apagado texto-pequeno">Universidad Nacional del Centro del Perú. Av. Mariscal Castilla 3909, El Tambo, Huancayo.</p>
        </div>
        <div>
          <p class="pie__titulo">Biblioteca</p>
          <ul class="pie__lista">
            <li><a href="catalogo.html">Catálogo</a></li>
            <li><a href="prestamos.html">Préstamos</a></li>
            <li><a href="perfil.html">Mi cuenta</a></li>
          </ul>
        </div>
        <div>
          <p class="pie__titulo">Integración</p>
          <ul class="pie__lista">
            <li><a href="${SERVIDOR}/api/docs/" target="_blank" rel="noopener">Swagger UI</a></li>
            <li><a href="${SERVIDOR}/api/redoc/" target="_blank" rel="noopener">ReDoc</a></li>
            <li><a href="${SERVIDOR}/api/schema/" target="_blank" rel="noopener">Esquema OpenAPI</a></li>
          </ul>
        </div>
        <div>
          <p class="pie__titulo">Horario</p>
          <ul class="pie__lista">
            <li><span>Lunes a viernes, 7:00 a 21:00</span></li>
            <li><span>Sábados, 8:00 a 14:00</span></li>
          </ul>
        </div>
      </div>
      <div class="contenedor pie__legal">
        <span>Facultad de Ingeniería de Sistemas</span>
        <span>Desarrollo de Aplicaciones Web · 2026</span>
      </div>
    </footer>`;
  }

  document.addEventListener("click", async (e) => {
    const boton = e.target.closest("[data-salir]");
    if (!boton) return;
    e.preventDefault();
    try {
      await Api.post("/auth/logout/");
    } catch (err) {}
    Sesion.cerrar();
    location.href = "index.html";
  });
})();