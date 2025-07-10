const container = document.getElementById("doctorContainer");

window.doctors.forEach(doc => {
    const card = document.createElement("div");
    card.className = "doctor-card";
    card.innerHTML = `
        <img src="${doc.image}" alt="${doc.name}" />
        <h3>${doc.name}</h3>
        <p>${doc.specialty}</p>
    `;
    container.appendChild(card);
});