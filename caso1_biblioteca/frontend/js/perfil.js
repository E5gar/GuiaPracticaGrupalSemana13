(function () {
  if (!Sesion.exigir()) return;

  const carnet = document.getElementById("carnet");
  const datos = document.getElementById("datos-perfil");
  const tabla = document.getElementById("tabla-historial");
  const envoltura = document.getElementById("envoltura-historial");
  const vacio = document.getElementById("vacio-historial");
  const formulario = document.getElementById("form-contacto");
  const errorForm = document.getElementById("error-contacto");
  let perfilActual = null;

  function pintarCarnet(p) {
    carnet.innerHTML = `
      <div class="carnet__logos">
        <img src="../../compartido/img/icon-uncp.png" alt="Lorem ipsum dolor">
        <img src="../../compartido/img/icon-fis.png" alt="Lorem ipsum dolor">
      </div>
      <p class="carnet__tipo">${TIPOS[p.tipo] || p.tipo}</p>
      <h2 class="carnet__nombre">${Util.escapar(p.nombre)}</h2>
      <dl class="carnet__datos">
        <div><dt>Usuario</dt><dd class="mono">${Util.escapar(p.username)}</dd></div>
        <div><dt>Carnet</dt><dd>${Util.escapar(p.carnet) || "-"}</dd></div>
        <div><dt>Carrera</dt><dd>${Util.escapar(p.carrera) || "-"}</dd></div>
        <div><dt>ID</dt><dd class="mono">#${p.id}</dd></div>
      </dl>`;
  }

  function pintarDatos(p) {
    const pendiente = p.historial_prestamos
      .filter((h) => h.estado !== "devuelto")
      .reduce((suma, h) => suma + Number(h.multa), 0);
    const cupo = Math.max(0, 5 - p.prestamos_activos);
    datos.innerHTML = `
      <div class="dato"><span class="dato__valor">${p.prestamos_activos}</span><span class="dato__nombre">Préstamos activos</span></div>
      <div class="dato"><span class="dato__valor">${cupo}</span><span class="dato__nombre">Cupo disponible</span></div>
      <div class="dato"><span class="dato__valor">${Util.soles(pendiente)}</span><span class="dato__nombre">Multa pendiente</span></div>`;
  }

  function pintarHistorial(lista) {
    envoltura.classList.toggle("oculto", lista.length === 0);
    vacio.classList.toggle("oculto", lista.length > 0);
    tabla.innerHTML = lista
      .map(
        (h) => `<tr>
          <td class="medio">${Util.escapar(h.libro_titulo)}</td>
          <td>${Util.fecha(h.fecha_prestamo)}</td>
          <td>${Util.fecha(h.fecha_devolucion)}</td>
          <td>${Util.etiquetaEstado(h.estado)}</td>
          <td class="num">${Util.soles(h.multa)}</td>
        </tr>`
      )
      .join("");
  }

  async function cargar() {
    try {
      perfilActual = await Api.get("/usuarios/perfil/");
      pintarCarnet(perfilActual);
      pintarDatos(perfilActual);
      pintarHistorial(perfilActual.historial_prestamos);
      formulario.elements.email.value = perfilActual.email || "";
      formulario.elements.telefono.value = perfilActual.telefono || "";
      UI.refrescarIconos();
    } catch (e) {
      if (e.estado === 401) Sesion.exigir();
      UI.aviso(e.message, "error");
    }
  }

  formulario.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorForm.classList.add("oculto");
    try {
      await Api.patch("/usuarios/" + perfilActual.id + "/", {
        email: formulario.elements.email.value.trim(),
        telefono: formulario.elements.telefono.value.trim()
      });
      UI.aviso("Datos actualizados", "ok");
      cargar();
    } catch (err) {
      errorForm.textContent = err.message;
      errorForm.classList.remove("oculto");
    }
  });

  cargar();
})();