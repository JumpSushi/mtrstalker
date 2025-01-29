let slideIndex = {
    pcb: 0,
    schematic: 0
};

function showSlide(index, carousel) {
    const slides = document.querySelectorAll(`.${carousel}-images img`);
    const totalSlides = slides.length;

    if (index >= totalSlides) {
        slideIndex[carousel] = 0;
    } else if (index < 0) {
        slideIndex[carousel] = totalSlides - 1;
    } else {
        slideIndex[carousel] = index;
    }
    const offset = -slideIndex[carousel] * 100;
    document.querySelector(`.${carousel}-images`).style.transform = `translateX(${offset}%)`;
}

function changeSlide(direction, carousel) {
    showSlide(slideIndex[carousel] + direction, carousel);
}

document.addEventListener('DOMContentLoaded', () => {
    showSlide(slideIndex.pcb, 'pcb');
    showSlide(slideIndex.schematic, 'schematic');
});