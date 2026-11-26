(function () {
  var CLAVE = "uncp-tema";
  var raiz = document.documentElement;

  function guardado() {
    try {
      return localStorage.getItem(CLAVE);
    } catch (e) {
      return null;
    }
  }

  function preferido() {
    var g = guardado();
    if (g === "claro" || g === "oscuro") return g;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "oscuro" : "claro";
  }

  function aplicar(tema, persistir) {
    raiz.setAttribute("data-tema", tema);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", tema === "oscuro" ? "#1a1917" : "#ffffff");
    document.querySelectorAll("[data-tema-toggle]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(tema === "oscuro"));
      b.setAttribute("aria-label", tema === "oscuro" ? "Cambiar a tema claro" : "Cambiar a tema oscuro");
    });
    if (persistir) {
      try {
        localStorage.setItem(CLAVE, tema);
      } catch (e) {}
    }
  }

  function alternar() {
    aplicar(raiz.getAttribute("data-tema") === "oscuro" ? "claro" : "oscuro", true);
  }

  function refrescarIconos() {
    if (window.lucide && typeof window.lucide.createIcons === "function") {
      window.lucide.createIcons();
    }
  }

  function crearContenedorAvisos() {
    var c = document.querySelector(".avisos");
    if (!c) {
      c = document.createElement("div");
      c.className = "avisos";
      c.setAttribute("role", "status");
      c.setAttribute("aria-live", "polite");
      document.body.appendChild(c);
    }
    return c;
  }

  function mostrarAviso(texto, tipo, duracion) {
    var c = crearContenedorAvisos();
    var a = document.createElement("div");
    a.className = "aviso" + (tipo ? " aviso--" + tipo : "");
    a.textContent = texto;
    c.appendChild(a);
    setTimeout(function () {
      a.style.opacity = "0";
      a.style.transition = "opacity 0.25s";
      setTimeout(function () {
        a.remove();
      }, 260);
    }, duracion || 3600);
  }

  function abrirModal(id) {
    var m = document.getElementById(id);
    if (!m) return;
    m.classList.add("modal--abierto");
    m.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    var foco = m.querySelector("input, select, textarea, button");
    if (foco) foco.focus();
  }

  function cerrarModal(m) {
    m.classList.remove("modal--abierto");
    m.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  function enlazarEventos() {
    document.addEventListener("click", function (e) {
      var t = e.target.closest("[data-tema-toggle]");
      if (t) {
        alternar();
        return;
      }

      var menu = e.target.closest("[data-menu-toggle]");
      if (menu) {
        var nav = document.getElementById(menu.getAttribute("aria-controls"));
        if (nav) {
          var abierto = nav.classList.toggle("cabecera__nav--abierta");
          menu.setAttribute("aria-expanded", String(abierto));
        }
        return;
      }

      var abrir = e.target.closest("[data-modal-abrir]");
      if (abrir) {
        abrirModal(abrir.getAttribute("data-modal-abrir"));
        return;
      }

      var cerrar = e.target.closest("[data-modal-cerrar]");
      if (cerrar) {
        var m = cerrar.closest(".modal");
        if (m) cerrarModal(m);
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      document.querySelectorAll(".modal--abierto").forEach(cerrarModal);
    });

    document.querySelectorAll(".anuncio__pista").forEach(function (pista) {
      if (pista.dataset.duplicada) return;
      pista.innerHTML = pista.innerHTML + pista.innerHTML;
      pista.dataset.duplicada = "1";
    });

    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    var cambio = function (ev) {
      if (!guardado()) aplicar(ev.matches ? "oscuro" : "claro", false);
    };
    if (mq.addEventListener) mq.addEventListener("change", cambio);
  }

  aplicar(preferido(), false);

  document.addEventListener("DOMContentLoaded", function () {
    aplicar(raiz.getAttribute("data-tema"), false);
    enlazarEventos();
    refrescarIconos();
  });

  window.UI = {
    aviso: mostrarAviso,
    abrirModal: abrirModal,
    cerrarModal: function (id) {
      var m = document.getElementById(id);
      if (m) cerrarModal(m);
    },
    refrescarIconos: refrescarIconos,
    tema: function () {
      return raiz.getAttribute("data-tema");
    }
  };
})();