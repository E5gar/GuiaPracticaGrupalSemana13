document.getElementById("form-login").addEventListener("submit", async (e) => {
  e.preventDefault();
  localStorage.removeItem(CLAVE_TOKEN);
  try {
    const datos = await pedir("/auth/token/", "POST", Object.fromEntries(new FormData(e.target)));
    localStorage.setItem(CLAVE_TOKEN, datos.token);
    location.href = "catalogo.html";
  } catch (error) {
    fallo(error);
  }
});
