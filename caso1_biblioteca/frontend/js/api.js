const SERVIDOR = "http://127.0.0.1:8000";
const API = SERVIDOR + "/api";
const CLAVE_TOKEN = "biblioteca-token";
const CLAVE_USUARIO = "biblioteca-usuario";

const Sesion = {
  token() {
    try {
      return localStorage.getItem(CLAVE_TOKEN);
    } catch (e) {
      return null;
    }
  },
  usuario() {
    try {
      return JSON.parse(localStorage.getItem(CLAVE_USUARIO));
    } catch (e) {
      return null;
    }
  },
  guardar(token, usuario) {
    try {
      localStorage.setItem(CLAVE_TOKEN, token);
      localStorage.setItem(CLAVE_USUARIO, JSON.stringify(usuario));
    } catch (e) {}
  },
  cerrar() {
    try {
      localStorage.removeItem(CLAVE_TOKEN);
      localStorage.removeItem(CLAVE_USUARIO);
    } catch (e) {}
  },
  activa() {
    return Boolean(this.token());
  },
  esPersonal() {
    const u = this.usuario();
    return Boolean(u && (u.es_admin || u.es_bibliotecario));
  },
  exigir() {
    if (this.activa()) return true;
    const actual = location.pathname.split("/").pop() + location.search;
    location.href = "login.html?volver=" + encodeURIComponent(actual);
    return false;
  }
};

class ErrorApi extends Error {
  constructor(estado, mensaje, detalle) {
    super(mensaje);
    this.estado = estado;
    this.detalle = detalle;
  }
}

function aplanarErrores(datos) {
  if (!datos) return "";
  if (typeof datos === "string") return datos;
  if (Array.isArray(datos)) return datos.map(aplanarErrores).join(" ");
  return Object.entries(datos)
    .map(([campo, valor]) => {
      const prefijo = campo === "detail" || campo === "non_field_errors" ? "" : campo + ": ";
      return prefijo + aplanarErrores(valor);
    })
    .join(" ");
}

async function pedir(metodo, ruta, { params, cuerpo } = {}) {
  let url = ruta.startsWith("http") ? ruta : API + ruta;
  if (params) {
    const consulta = new URLSearchParams();
    Object.entries(params).forEach(([clave, valor]) => {
      if (valor !== "" && valor !== null && valor !== undefined && valor !== false) consulta.set(clave, valor);
    });
    const texto = consulta.toString();
    if (texto) url += (url.includes("?") ? "&" : "?") + texto;
  }
  const cabeceras = { Accept: "application/json" };
  if (cuerpo !== undefined) cabeceras["Content-Type"] = "application/json";
  const token = Sesion.token();
  if (token) cabeceras.Authorization = "Token " + token;

  let respuesta;
  try {
    respuesta = await fetch(url, {
      method: metodo,
      headers: cabeceras,
      body: cuerpo !== undefined ? JSON.stringify(cuerpo) : undefined
    });
  } catch (e) {
    throw new ErrorApi(0, "No se pudo conectar con el servidor.");
  }

  if (respuesta.status === 204) return null;
  let datos = null;
  try {
    datos = await respuesta.json();
  } catch (e) {}

  if (!respuesta.ok) {
    if (respuesta.status === 401 && token) Sesion.cerrar();
    if (respuesta.status === 429) {
      throw new ErrorApi(429, "Demasiadas solicitudes seguidas. Espera unos segundos e inténtalo otra vez.", datos);
    }
    throw new ErrorApi(respuesta.status, aplanarErrores(datos) || "Ocurrió un error inesperado.", datos);
  }
  return datos;
}

const Api = {
  get: (ruta, params) => pedir("GET", ruta, { params }),
  post: (ruta, cuerpo) => pedir("POST", ruta, { cuerpo: cuerpo === undefined ? {} : cuerpo }),
  patch: (ruta, cuerpo) => pedir("PATCH", ruta, { cuerpo })
};

const TIPOS = {
  administrador: "Administrador",
  bibliotecario: "Bibliotecario",
  estudiante: "Estudiante",
  docente: "Docente",
  investigador: "Investigador"
};

const Util = {
  escapar(texto) {
    const mapa = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
    return String(texto === null || texto === undefined ? "" : texto).replace(/[&<>"']/g, (c) => mapa[c]);
  },
  fecha(iso) {
    if (!iso) return "-";
    const [a, m, d] = iso.split("-");
    return d + "/" + m + "/" + a;
  },
  soles(valor) {
    return "S/ " + Number(valor).toFixed(2);
  },
  retraso(funcion, ms = 350) {
    let temporizador;
    return (...args) => {
      clearTimeout(temporizador);
      temporizador = setTimeout(() => funcion(...args), ms);
    };
  },
  etiquetaEstado(estado) {
    const clases = { activo: "etiqueta--info", vencido: "etiqueta--error", devuelto: "etiqueta--ok" };
    const textos = { activo: "Activo", vencido: "Vencido", devuelto: "Devuelto" };
    return `<span class="etiqueta ${clases[estado] || ""}">${textos[estado] || estado}</span>`;
  },
  fichaLibro(l) {
    const hay = l.disponible;
    return `<article class="tarjeta">
      <div class="tarjeta__media">
        <img src="${Util.escapar(l.portada)}" alt="Lorem ipsum dolor" loading="lazy">
        <span class="tarjeta__insignia etiqueta ${hay ? "etiqueta--ok" : "etiqueta--error"}">${hay ? "Disponible" : "Agotado"}</span>
      </div>
      <div class="tarjeta__cuerpo">
        <h3 class="tarjeta__titulo">${Util.escapar(l.titulo)}</h3>
        <p class="tarjeta__meta">${Util.escapar(l.autor.nombre)} · ${l.anio}</p>
        <p class="tarjeta__meta ficha__ubicacion"><i data-lucide="map-pin" class="icono--chico"></i>${Util.escapar(l.ubicacion)}</p>
        <div class="tarjeta__pie ficha__pie">
          <a class="boton boton--chico boton--ancho" href="catalogo.html?libro=${l.id}" data-ver="${l.id}">Ver ficha</a>
        </div>
      </div>
    </article>`;
  }
};