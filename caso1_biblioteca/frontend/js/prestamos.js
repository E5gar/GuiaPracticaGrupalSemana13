(function () {
  if (!Sesion.exigir()) return;

  const personal = Sesion.esPersonal();
  const LIMITE = 10;
  const estado = { pestana: "todos", offset: 0 };

  const cuerpo = document.getElementById("tabla-prestamos");
  const cabecera = document.getElementById("cabecera-tabla");
  const envoltura = document.getElementById("envoltura-tabla");
  const vacio = document.getElementById("vacio-prestamos");
  const info = document.getElementById("info-paginas");
  const anterior = document.getElementById("pagina-anterior");
  const siguiente = document.getElementById("pagina-siguiente");
  const datoActivos = document.getElementById("dato-activos");
  const datoVencidos = document.getElementById("dato-vencidos");
  const datoMulta = document.getElementById("dato-multa");
  const formulario = document.getElementById("form-prestamo");
  const errorForm = document.getElementById("error-prestamo");
  const buscarLibro = document.getElementById("p-buscar");
  const selectLibro = document.getElementById("p-libro");
  const campoFecha = document.getElementById("p-fecha");

  const columnas = ["Libro", personal ? "Usuario" : null, "Prestado", "Vence", "Estado", "Plazo", "Multa", personal ? "Acción" : null].filter(Boolean);
  cabecera.innerHTML = columnas.map((c, i) => `<th${c === "Multa" ? ' class="num"' : ""}>${c}</th>`).join("");

  if (personal) {
    document.getElementById("abrir-registro").classList.remove("oculto");
    document.getElementById("titulo-prestamos").textContent = "Préstamos de la biblioteca";
  }
  campoFecha.min = new Date().toISOString().slice(0, 10);

  function plazo(p) {
    if (p.estado === "devuelto") return "-";
    if (p.dias_restantes < 0) return Math.abs(p.dias_restantes) + " d de atraso";
    return p.dias_restantes + " d";
  }

  function fila(p) {
    const abierto = p.estado !== "devuelto";
    return `<tr>
      <td class="medio">${Util.escapar(p.libro_titulo)}</td>
      ${personal ? `<td>${Util.escapar(p.usuario_nombre)} <span class="texto-apagado mono">#${p.usuario}</span></td>` : ""}
      <td>${Util.fecha(p.fecha_prestamo)}</td>
      <td>${Util.fecha(p.fecha_devolucion)}</td>
      <td>${Util.etiquetaEstado(p.estado)}</td>
      <td>${plazo(p)}</td>
      <td class="num">${Util.soles(p.multa)}</td>
      ${personal ? `<td>${abierto ? `<button class="boton boton--chico" type="button" data-devolver="${p.id}">Devolver</button>` : ""}</td>` : ""}
    </tr>`;
  }

  function pintar(datos) {
    const filas = datos.results;
    cuerpo.innerHTML = filas.map(fila).join("");
    vacio.classList.toggle("oculto", filas.length > 0);
    envoltura.classList.toggle("oculto", filas.length === 0);
    const desde = filas.length ? estado.offset + 1 : 0;
    info.textContent = desde + "-" + (estado.offset + filas.length) + " de " + datos.count;
    anterior.disabled = estado.offset === 0;
    siguiente.disabled = estado.offset + LIMITE >= datos.count;
    datoMulta.textContent = Util.soles(filas.reduce((suma, p) => suma + Number(p.multa), 0));
    UI.refrescarIconos();
  }

  async function cargar() {
    const params = { limit: LIMITE, offset: estado.offset };
    let ruta = "/prestamos/";
    if (estado.pestana === "vencido" && personal) {
      ruta = "/prestamos/vencidos/";
    } else if (estado.pestana !== "todos") {
      params.estado = estado.pestana;
    }
    try {
      pintar(await Api.get(ruta, params));
    } catch (e) {
      if (e.estado === 401) Sesion.exigir();
      UI.aviso(e.message, "error");
    }
  }

  async function cargarResumen() {
    try {
      const [activos, vencidos] = await Promise.all([
        Api.get("/prestamos/", { estado: "activo", limit: 1 }),
        Api.get("/prestamos/", { estado: "vencido", limit: 1 })
      ]);
      datoActivos.textContent = activos.count;
      datoVencidos.textContent = vencidos.count;
    } catch (e) {
      datoActivos.textContent = "-";
      datoVencidos.textContent = "-";
    }
  }

  async function buscarLibros(texto) {
    try {
      const datos = await Api.get("/libros/", { search: texto, disponible: true, tamano: 10 });
      selectLibro.innerHTML = datos.results.length
        ? datos.results.map((l) => `<option value="${l.id}">${Util.escapar(l.titulo)} (${l.stock})</option>`).join("")
        : '<option value="">Sin resultados</option>';
    } catch (e) {
      UI.aviso(e.message, "error");
    }
  }

  document.querySelectorAll("[data-pestana]").forEach((boton) => {
    boton.addEventListener("click", () => {
      estado.pestana = boton.dataset.pestana;
      estado.offset = 0;
      document.querySelectorAll("[data-pestana]").forEach((b) => b.setAttribute("aria-selected", String(b === boton)));
      cargar();
    });
  });

  anterior.addEventListener("click", () => {
    estado.offset = Math.max(0, estado.offset - LIMITE);
    cargar();
  });
  siguiente.addEventListener("click", () => {
    estado.offset += LIMITE;
    cargar();
  });

  cuerpo.addEventListener("click", async (e) => {
    const boton = e.target.closest("[data-devolver]");
    if (!boton) return;
    if (!window.confirm("¿Confirmas que el libro fue devuelto?")) return;
    boton.disabled = true;
    try {
      await Api.post("/prestamos/" + boton.dataset.devolver + "/devolver/");
      UI.aviso("Devolución registrada", "ok");
      await Promise.all([cargar(), cargarResumen()]);
    } catch (err) {
      UI.aviso(err.message, "error");
      boton.disabled = false;
    }
  });

  buscarLibro.addEventListener("input", Util.retraso(() => buscarLibros(buscarLibro.value.trim())));

  formulario.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorForm.classList.add("oculto");
    const peticion = {
      usuario: Number(formulario.elements.usuario.value),
      libro: Number(selectLibro.value)
    };
    if (formulario.elements.fecha.value) peticion.fecha_devolucion = formulario.elements.fecha.value;
    try {
      await Api.post("/prestamos/", peticion);
      UI.cerrarModal("modal-prestamo");
      formulario.reset();
      UI.aviso("Préstamo registrado", "ok");
      estado.offset = 0;
      await Promise.all([cargar(), cargarResumen()]);
    } catch (err) {
      errorForm.textContent = err.message;
      errorForm.classList.remove("oculto");
    }
  });

  const libroUrl = new URLSearchParams(location.search).get("libro");
  if (personal && libroUrl) {
    Api.get("/libros/" + libroUrl + "/")
      .then((l) => {
        selectLibro.innerHTML = `<option value="${l.id}">${Util.escapar(l.titulo)} (${l.stock})</option>`;
        UI.abrirModal("modal-prestamo");
      })
      .catch((err) => UI.aviso(err.message, "error"));
  }

  cargar();
  cargarResumen();
})();