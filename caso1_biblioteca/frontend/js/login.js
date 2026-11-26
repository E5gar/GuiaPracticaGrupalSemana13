(function () {
  const formulario = document.getElementById("form-login");
  const error = document.getElementById("error-login");
  const enviar = document.getElementById("enviar-login");
  const clave = document.getElementById("l-clave");
  const ver = document.getElementById("ver-clave");

  if (Sesion.activa()) {
    location.replace("index.html");
    return;
  }

  ver.addEventListener("click", () => {
    const visible = clave.type === "text";
    clave.type = visible ? "password" : "text";
    ver.setAttribute("aria-label", visible ? "Mostrar contraseña" : "Ocultar contraseña");
    ver.innerHTML = `<i data-lucide="${visible ? "eye" : "eye-off"}" class="icono--chico"></i>`;
    UI.refrescarIconos();
  });

  formulario.addEventListener("submit", async (e) => {
    e.preventDefault();
    error.classList.add("oculto");
    const username = formulario.elements.username.value.trim();
    const password = formulario.elements.password.value;
    if (!username || !password) {
      error.textContent = "Escribe tu usuario y tu contraseña.";
      error.classList.remove("oculto");
      return;
    }
    enviar.disabled = true;
    try {
      const respuesta = await Api.post("/auth/token/", { username, password });
      Sesion.guardar(respuesta.token, respuesta.usuario);
      const volver = new URLSearchParams(location.search).get("volver");
      location.href = volver && !volver.startsWith("http") ? volver : "index.html";
    } catch (err) {
      error.textContent = err.estado === 400 ? "Usuario o contraseña incorrectos." : err.message;
      error.classList.remove("oculto");
      enviar.disabled = false;
    }
  });
})();