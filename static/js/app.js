document.addEventListener(
    "DOMContentLoaded",
    function () {

        inicializarBusquedas();

        inicializarConfirmaciones();

        inicializarValidacion();

        inicializarTooltips();

        inicializarReloj();

        inicializarRegistro();

        inicializarNotificaciones();

    }
);


function inicializarBusquedas() {

    const buscadores = document.querySelectorAll(
        "[data-buscador]"
    );

    buscadores.forEach(
        function (buscador) {

            buscador.addEventListener(
                "input",
                function () {

                    const texto =
                        buscador.value
                        .toLowerCase()
                        .trim();

                    const filas =
                        document.querySelectorAll(
                            buscador.dataset.buscador
                        );

                    filas.forEach(
                        function (fila) {

                            const contenido =
                                fila.textContent
                                .toLowerCase();

                            fila.style.display =
                                contenido.includes(texto)
                                    ? ""
                                    : "none";

                        }
                    );

                }
            );

        }
    );

}


function inicializarConfirmaciones() {

    const elementos =
        document.querySelectorAll(
            "[data-confirmar]"
        );

    elementos.forEach(
        function (elemento) {

            elemento.addEventListener(
                "click",
                function (evento) {

                    const mensaje =
                        elemento.dataset.confirmar;

                    if (!confirm(mensaje)) {

                        evento.preventDefault();

                    }

                }
            );

        }
    );

}


function inicializarValidacion() {

    const formularios =
        document.querySelectorAll(
            ".needs-validation"
        );

    formularios.forEach(
        function (formulario) {

            formulario.addEventListener(
                "submit",
                function (evento) {

                    if (!formulario.checkValidity()) {

                        evento.preventDefault();
                        evento.stopPropagation();

                    }

                    formulario.classList.add(
                        "was-validated"
                    );

                }
            );

        }
    );

}


function inicializarTooltips() {

    const elementos =
        document.querySelectorAll(
            '[data-bs-toggle="tooltip"]'
        );

    elementos.forEach(
        function (elemento) {

            new bootstrap.Tooltip(elemento);

        }
    );

}


function inicializarReloj() {

    const reloj =
        document.getElementById(
            "relojSistema"
        );

    if (!reloj) {
        return;
    }

    function actualizar() {

        const ahora = new Date();

        reloj.textContent =
            ahora.toLocaleString(
                "es-MX",
                {
                    dateStyle: "medium",
                    timeStyle: "short"
                }
            );

    }

    actualizar();

    setInterval(
        actualizar,
        1000
    );

}


function inicializarRegistro() {

    const password =
        document.getElementById(
            "passwordRegistro"
        );

    const confirmar =
        document.getElementById(
            "confirmarPassword"
        );

    if (!password || !confirmar) {
        return;
    }

    function validar() {

        if (
            confirmar.value !== "" &&
            password.value !== confirmar.value
        ) {

            confirmar.setCustomValidity(
                "Las contraseñas no coinciden."
            );

        } else {

            confirmar.setCustomValidity(
                ""
            );

        }

    }

    password.addEventListener(
        "input",
        validar
    );

    confirmar.addEventListener(
        "input",
        validar
    );

}


function inicializarNotificaciones() {

    const botones =
        document.querySelectorAll(
            "[data-notificacion]"
        );

    botones.forEach(
        function (boton) {

            boton.addEventListener(
                "click",
                function () {

                    const contenedor =
                        document.getElementById(
                            "contenedorNotificaciones"
                        );

                    if (!contenedor) {
                        return;
                    }

                    const alerta =
                        document.createElement(
                            "div"
                        );

                    alerta.className =
                        "alert alert-success " +
                        "alert-dismissible fade show";

                    alerta.innerHTML = `
                        <i class="bi bi-check-circle-fill me-2"></i>
                        ${boton.dataset.notificacion}
                        <button
                            type="button"
                            class="btn-close btn-close-white"
                            data-bs-dismiss="alert"
                        ></button>
                    `;

                    contenedor.appendChild(
                        alerta
                    );

                    setTimeout(
                        function () {
                            alerta.remove();
                        },
                        5000
                    );

                }
            );

        }
    );

}
document.addEventListener(
    "DOMContentLoaded",
    function () {

        inicializarRegistro();
        inicializarConfirmaciones();
        inicializarBuscadores();
        inicializarNotificaciones();

    }
);


/* =====================================
   REGISTRO DE USUARIO
===================================== */

function inicializarRegistro() {

    const formulario = document.getElementById(
        "formRegistro"
    );

    if (!formulario) {
        return;
    }

    const nombre = document.getElementById("nombre");
    const correo = document.getElementById("correo");
    const password = document.getElementById(
        "passwordRegistro"
    );
    const confirmarPassword = document.getElementById(
        "confirmarPassword"
    );
    const terminos = document.getElementById("terminos");
    const botonMostrar = document.getElementById(
        "mostrarPassword"
    );
    const contenedorError = document.getElementById(
        "errorRegistro"
    );

    if (botonMostrar) {

        botonMostrar.addEventListener(
            "click",
            function () {

                const mostrar =
                    password.type === "password";

                password.type = mostrar
                    ? "text"
                    : "password";

                confirmarPassword.type = mostrar
                    ? "text"
                    : "password";

                botonMostrar.innerHTML = mostrar
                    ? '<i class="bi bi-eye-slash"></i>'
                    : '<i class="bi bi-eye"></i>';

            }
        );

    }

    confirmarPassword.addEventListener(
        "input",
        function () {

            if (
                confirmarPassword.value !== password.value
            ) {
                confirmarPassword.setCustomValidity(
                    "Las contraseñas no coinciden."
                );
            } else {
                confirmarPassword.setCustomValidity("");
            }

        }
    );

    password.addEventListener(
        "input",
        function () {

            if (
                confirmarPassword.value !== "" &&
                confirmarPassword.value !== password.value
            ) {
                confirmarPassword.setCustomValidity(
                    "Las contraseñas no coinciden."
                );
            } else {
                confirmarPassword.setCustomValidity("");
            }

        }
    );

    formulario.addEventListener(
        "submit",
        function (evento) {

            const errores = [];

            contenedorError.innerHTML = "";

            if (nombre.value.trim().length < 3) {
                errores.push(
                    "El nombre debe tener al menos 3 caracteres."
                );
            }

            if (
                !correo.value.includes("@") ||
                !correo.value.includes(".")
            ) {
                errores.push(
                    "Escribe un correo electrónico válido."
                );
            }

            if (password.value.length < 6) {
                errores.push(
                    "La contraseña debe tener mínimo 6 caracteres."
                );
            }

            if (
                password.value !== confirmarPassword.value
            ) {
                errores.push(
                    "Las contraseñas no coinciden."
                );
            }

            if (!terminos.checked) {
                errores.push(
                    "Debes aceptar el uso de tus datos."
                );
            }

            if (errores.length > 0) {

                evento.preventDefault();

                let listaErrores = `
                    <div class="alert alert-danger">
                        <strong>
                            Revisa el formulario:
                        </strong>
                        <ul class="mb-0 mt-2">
                `;

                errores.forEach(
                    function (error) {
                        listaErrores += `
                            <li>${error}</li>
                        `;
                    }
                );

                listaErrores += `
                        </ul>
                    </div>
                `;

                contenedorError.innerHTML = listaErrores;

                return;
            }

            const boton = document.getElementById(
                "botonRegistro"
            );

            boton.disabled = true;

            boton.innerHTML = `
                <span
                    class="spinner-border spinner-border-sm"
                ></span>
                Registrando usuario...
            `;

        }
    );

}


/* =====================================
   CONFIRMACIÓN DE ELIMINACIÓN
===================================== */

function inicializarConfirmaciones() {

    const elementos = document.querySelectorAll(
        "[data-confirmar]"
    );

    elementos.forEach(
        function (elemento) {

            elemento.addEventListener(
                "click",
                function (evento) {

                    const mensaje =
                        elemento.dataset.confirmar;

                    const confirmar = confirm(mensaje);

                    if (!confirmar) {
                        evento.preventDefault();
                    }

                }
            );

        }
    );

}


/* =====================================
   BÚSQUEDA EN TABLAS
===================================== */

function inicializarBuscadores() {

    const buscadores = document.querySelectorAll(
        "[data-buscador]"
    );

    buscadores.forEach(
        function (buscador) {

            buscador.addEventListener(
                "input",
                function () {

                    const texto =
                        buscador.value
                        .toLowerCase()
                        .trim();

                    const filas = document.querySelectorAll(
                        buscador.dataset.buscador
                    );

                    filas.forEach(
                        function (fila) {

                            const contenido =
                                fila.textContent
                                .toLowerCase();

                            fila.style.display =
                                contenido.includes(texto)
                                    ? ""
                                    : "none";

                        }
                    );

                }
            );

        }
    );

}


/* =====================================
   NOTIFICACIONES
===================================== */

function inicializarNotificaciones() {

    const botones = document.querySelectorAll(
        "[data-notificacion]"
    );

    botones.forEach(
        function (boton) {

            boton.addEventListener(
                "click",
                function () {

                    const contenedor =
                        document.getElementById(
                            "contenedorNotificaciones"
                        );

                    if (!contenedor) {
                        return;
                    }

                    const alerta =
                        document.createElement("div");

                    alerta.className =
                        "alert alert-success " +
                        "alert-dismissible fade show";

                    alerta.innerHTML = `
                        <i class="bi bi-check-circle-fill me-2"></i>
                        ${boton.dataset.notificacion}

                        <button
                            type="button"
                            class="btn-close btn-close-white"
                            data-bs-dismiss="alert"
                        ></button>
                    `;

                    contenedor.appendChild(alerta);

                    setTimeout(
                        function () {
                            alerta.remove();
                        },
                        5000
                    );

                }
            );

        }
    );

}