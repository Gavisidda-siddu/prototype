const services = [
    {
        title: "Diagnostic Services",
        image: "{{ url_for('static', filename='images/diagnosticservice.jpg') }}",
        items: [
            "Electrocardiogram (ECG or EKG) – Measures electrical activity of the heart.",
            "Echocardiogram – Uses ultrasound to visualize heart function and structure.",
            "Stress Testing (TMT) – Evaluates heart function during physical exertion.",
            "Holter Monitoring – 24–48 hour continuous ECG monitoring.",
            "Cardiac MRI and CT Scan – Advanced imaging for detailed heart structure.",
            "Coronary Angiography – Checks for blockages in the coronary arteries.",
            "Blood Tests – For cardiac markers like troponin, cholesterol, etc."
        ]
    },
    {
        title: "Interventional Cardiology",
        image: "{{ url_for('static', filename='images/intervential cardiology.jpg') }}",
        items: [
            "Angioplasty (with or without stent placement)",
            "Coronary Artery Bypass Grafting (CABG)",
            "Pacemaker and ICD insertion",
            "Valve Repair or Replacement (TAVR, Mitral Clip)",
            "Electrophysiology Studies and Ablation for arrhythmias"
        ]
    },
    {
        title: "Cardiac Surgery",
        image: "{{ url_for('static', filename='images/cardiac surgery.jpg') }}",
        items: [
            "Open-heart surgery",
            "Valve replacement surgeries",
            "Congenital heart defect correction",
            "Heart transplant (in some advanced centers)"
        ]
    },
    {
        title: "Outpatient & Preventive Cardiology",
        image: "{{ url_for('static', filename='images/outpatient.jpg') }}",
        items: [
            "Heart check-up packages",
            "Lipid profile monitoring and hypertension control",
            "Lifestyle counseling (diet, exercise, smoking cessation)",
            "Cardiac rehabilitation programs"
        ]
    },
    {
        title: "Emergency Cardiac Care",
        image: "{{ url_for('static', filename='images/emergency.webp') }}",
        items: [
            "24/7 Cardiac Emergency Unit",
            "Management of acute heart attack (STEMI/NSTEMI)",
            "Advanced life support systems and defibrillation"
        ]
    },
    {
        title: "Pediatric Cardiology",
        image: "{{ url_for('static', filename='images/pediatric.jpg') }}",
        items: [
            "Diagnosis and treatment of congenital heart diseases in children",
            "Fetal echocardiography (for prenatal diagnosis)",
            "Surgical and catheter-based interventions in children"
        ]
    },
    {
        title: "Electrophysiology and Arrhythmia Management",
        image: "{{ url_for('static', filename='images/electrop.jpg') }}",
        items: [
            "Diagnosis and treatment of abnormal heart rhythms",
            "Ablation therapy",
            "Pacemaker and ICD implantation"
        ]
    },
    {
        title: "Heart Failure Clinics",
        image: "{{ url_for('static', filename='images/heart failure.png') }}",
        items: [
            "Advanced therapies for chronic heart failure",
            "Device therapy (CRT, LVAD)",
            "Transplant assessment and care"
        ]
    },
    {
        title: "Telecardiology & Remote Monitoring",
        image: "{{ url_for('static', filename='images/telehealth.png') }}",
        items: [
            "Remote ECG monitoring",
            "Teleconsultations for follow-up care"
        ]
    },
    {
        title: "Specialized Units",
        image: "{{ url_for('static', filename='images/specialized.jpg') }}",
        items: [
            "Cardiac Intensive Care Unit (CICU)",
            "Post-operative cardiac care",
            "Cardiac catheterization lab (Cath Lab)"
        ]
    }
];

const container = document.getElementById("card-container");

services.forEach(service => {
    const card = document.createElement("div");
    card.className = "card";

    const listItems = service.items.map(item => `<li>${item}</li>`).join("");

    card.innerHTML = `
        <img src="${service.image}" alt="${service.title}" />
        <div class="card-body">
            <h3>${service.title}</h3>
            <ul>${listItems}</ul>
        </div>
    `;

    container.appendChild(card);
});