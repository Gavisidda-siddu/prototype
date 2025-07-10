const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.dot');
let currentIndex = 0;
let interval = setInterval(nextSlide, 5000); // 5 seconds

function showSlide(index) {
    slides.forEach((slide, i) => {
        slide.classList.toggle('active', i === index);
        dots[i].classList.toggle('active', i === index);
    });
    currentIndex = index;
}

function nextSlide() {
    let nextIndex = (currentIndex + 1) % slides.length;
    showSlide(nextIndex);
}

function goToSlide(index) {
    clearInterval(interval);
    showSlide(index);
    interval = setInterval(nextSlide, 5000);
}

let currentSlide = 0;
const slides2 = document.querySelector('.slides2');
const dots2 = document.querySelectorAll('.dot2');

function moveToSlide(slideIndex) {
    currentSlide = slideIndex;
    const offset = -100 * slideIndex;
    slides2.style.transform = `translateX(${offset}%)`;

    dots2.forEach(dot => dot.classList.remove('active'));
    dots2[slideIndex].classList.add('active');
}

setInterval(() => {
    currentSlide = (currentSlide + 1) % dots2.length;
    moveToSlide(currentSlide);
}, 5000);