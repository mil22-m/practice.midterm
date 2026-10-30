const API_URL = "http://<IP-PUBLICA-DE-TU-EC2>:8000"; // Cambiarás esto luego por la IP de EC2

document.getElementById("shorten-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const originalUrl = document.getElementById("original-url").value;
    const resultDiv = document.getElementById("result");
    const errorDiv = document.getElementById("error-msg");
    
    resultDiv.classList.add("hidden");
    errorDiv.classList.add("hidden");

    try {
        const response = await fetch(`${API_URL}/shorten`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ original_url: originalUrl })
        });

        if (!response.ok) throw new Error("Error al conectar con el servidor.");

        const data = await response.json();
        
        document.getElementById("short-url-output").value = data.short_url;
        resultDiv.classList.remove("hidden");
    } catch (err) {
        errorDiv.textContent = "No se pudo acortar el enlace. Verifica que el backend esté activo.";
        errorDiv.classList.remove("hidden");
    }
});

document.getElementById("copy-btn").addEventListener("click", () => {
    const copyText = document.getElementById("short-url-output");
    copyText.select();
    document.execCommand("copy");
    alert("¡Enlace copiado al portapapeles!");
});