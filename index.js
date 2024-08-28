document.getElementById('formCores').addEventListener('submit', function(event) {
    event.preventDefault(); // Evita que el formulario se envíe de la manera tradicional

    let formData = new FormData(this); // Recoge los datos del formulario

    fetch('http://127.0.0.1:5000/procesarcores', { // Asegúrate de que la URL sea la correcta de tu API
        method: 'POST',
        body: formData
    })
    .then(response => response.json()) // Asume que la API responde con JSON
    .then(data => {
        alert(`${data.mensaje},${data.numCores} `)
    })
    .catch(error => {
        console.log("error", error)
    });
});