// static/js/carrusel.js

function moverCarrusel(idCarrusel, distancia) {
    const contenedor = document.getElementById(idCarrusel);
    // Desplaza el contenido horizontalmente de forma suave
    contenedor.scrollLeft += distancia;
}