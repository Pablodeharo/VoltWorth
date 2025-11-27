console.log("🚗 vehicles.js loaded");

// 6 modelos predefinidos
const carModels = [
    {
        name: "Tesla Model 3 – Finlandia",
        country: "Finland",
        brand: "TESLA",
        model: "MODEL 3 LONG RANGE",
        battery: 75,
        range: 500,
        torque: 450,
        topspeed: 233,
        seats: 5,
        drivetrain: "AWD",
        body: "Sedan",
        age: 2,
        km: 30000
    },
    {
        name: "Volkswagen ID.7 – Alemania",
        country: "Germany",
        brand: "VOLKSWAGEN",
        model: "ID.7 GTX",
        battery: 86,
        range: 500,
        torque: 560,
        topspeed: 180,
        seats: 5,
        drivetrain: "AWD",
        body: "Liftback Sedan",
        age: 2,
        km: 30915
    },
    {
        name: "Mercedes EQE – España",
        country: "Spain",
        brand: "MERCEDES-BENZ",
        model: "EQE 350 4MATIC",
        battery: 90.6,
        range: 515,
        torque: 765,
        topspeed: 210,
        seats: 5,
        drivetrain: "AWD",
        body: "Sedan",
        age: 3,
        km: 38843
    },
    {
        name: "BYD Dolphin – Bélgica",
        country: "Belgium",
        brand: "BYD",
        model: "DOLPHIN 60.4 KWH",
        battery: 60.5,
        range: 350,
        torque: 310,
        topspeed: 160,
        seats: 5,
        drivetrain: "FWD",
        body: "Hatchback",
        age: 3,
        km: 42368
    },
    {
        name: "Peugeot E-208 – Francia",
        country: "France",
        brand: "PEUGEOT",
        model: "E-208 50 KWH",
        battery: 46.3,
        range: 290,
        torque: 260,
        topspeed: 150,
        seats: 5,
        drivetrain: "FWD",
        body: "Hatchback",
        age: 2,
        km: 38612
    },
    {
        name: "Audi Q4 E-tron – Alemania",
        country: "Germany",
        brand: "AUDI",
        model: "Q4 E-TRON 45",
        battery: 77,
        range: 420,
        torque: 545,
        topspeed: 180,
        seats: 5,
        drivetrain: "RWD",
        body: "SUV",
        age: 1,
        km: 17916
    }
];

// Variable para guardar el país seleccionado
let selectedCountry = "";

// === GENERAR CARDS ===
function buildCards() {
    const container = document.getElementById("carCardsContainer");
    container.innerHTML = "";

    carModels.forEach((car, index) => {
        container.innerHTML += `
        <div class="col-md-4 mb-3">
            <div class="card p-3 shadow-sm card-car" style="cursor:pointer; border:2px solid transparent;" onclick="selectModel(${index})">
                <strong>${car.name}</strong><br>
                <span class="text-secondary">${car.brand} ${car.model}</span>
            </div>
        </div>`;
    });
}
buildCards();

// === AUTO RELLENADO ===
window.selectModel = function(i) {
    const c = carModels[i];

    // Guardar el país seleccionado
    selectedCountry = c.country;

    document.getElementById("brand").value = c.brand;
    document.getElementById("model").value = c.model;
    document.getElementById("battery").value = c.battery;
    document.getElementById("range").value = c.range;
    document.getElementById("torque").value = c.torque;
    document.getElementById("topspeed").value = c.topspeed;
    document.getElementById("seats").value = c.seats;
    document.getElementById("drivetrain").value = c.drivetrain;
    document.getElementById("body").value = c.body;
    document.getElementById("age").value = c.age;
    document.getElementById("km").value = c.km;

    document.querySelectorAll(".card-car").forEach(c => c.style.border = "2px solid transparent");
    document.querySelectorAll(".card-car")[i].style.border = "2px solid #3B5BFF";
};

// === ENVÍO ===
document.getElementById("predictionForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const payload = {
        brand: document.getElementById("brand").value,
        model: document.getElementById("model").value,
        country: selectedCountry || "Spain",  // ⚠️ IMPORTANTE: país seleccionado
        battery_capacity_kWh: parseFloat(document.getElementById("battery").value),
        electric_range_km: parseFloat(document.getElementById("range").value),
        torque_nm: parseFloat(document.getElementById("torque").value),
        top_speed_kmh: parseFloat(document.getElementById("topspeed").value),
        seats: parseFloat(document.getElementById("seats").value),
        drivetrain: document.getElementById("drivetrain").value,
        car_body_type: document.getElementById("body").value,
        age_years: parseFloat(document.getElementById("age").value),
        km: parseFloat(document.getElementById("km").value)
    };

    console.log("📤 Enviando payload:", payload);

    try {
        const response = await fetch("/api/predict/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("📥 Respuesta recibida:", data);

        const pricesNode = document.getElementById("prices");
        pricesNode.innerHTML = "";

        // Mostrar resultados
        Object.entries(data).forEach(([country, value]) => {
            pricesNode.innerHTML += `
                <div class="mb-2">
                    <strong>${country}:</strong> 
                    <span class="text-success fs-5">${value.toLocaleString('es-ES')} €</span>
                </div>`;
        });

        document.getElementById("priceResults").style.display = "block";

    } catch (error) {
        console.error("❌ Error:", error);
        alert("Error al realizar la predicción: " + error.message);
    }
});

// Función para obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}