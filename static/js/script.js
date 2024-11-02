const bilist = document.querySelector(".bi-list");
const menumobile = document.querySelector(".menu-mobile");
const close = document.querySelector(".bi-x");

bilist.addEventListener("click", () => {
    menumobile.classList.add("animate__fadeIn");
    menumobile.classList.remove("animate__fadeOut");
    menumobile.classList.add("d-flex");
});

close.addEventListener("click", () => {
    menumobile.classList.add("animate__fadeOut");
    menumobile.classList.remove("animate__fadeIn");
    setTimeout(() => {
        menumobile.classList.remove("d-flex");
    }, 500);
    close.classList.add("rotate");
    setTimeout(() => {
        close.classList.remove("rotate");
    }, 400);
});

document.addEventListener("click", (e) => {
    if (!menumobile.contains(e.target) && !bilist.contains(e.target)) {
        menumobile.classList.add("animate__fadeOut");
        menumobile.classList.remove("animate__fadeIn");
        setTimeout(() => {
            menumobile.classList.remove("d-flex");
        }, 500);
    }
});

const supportButton = document.getElementById('supportButton');
const supportMenu = document.getElementById('supportMenu');
const buttonIcon = document.getElementById('buttonIcon');
const overlay = document.getElementById('overlay');

supportButton.addEventListener('click', () => {
    if (supportMenu.classList.contains('d-flex')) {
        supportMenu.style.opacity = '0';
        overlay.style.opacity = '0';
        setTimeout(() => {
            supportMenu.classList.remove('d-flex');
            supportMenu.classList.add('d-none');
            overlay.style.display = 'none';
        }, 300);
        buttonIcon.classList.remove('bi-x');
        buttonIcon.classList.add('bi-whatsapp');
    } else {
        supportMenu.classList.remove('d-none');
        supportMenu.classList.add('d-flex');
        overlay.style.display = 'block';
        setTimeout(() => {
            supportMenu.style.opacity = '1';
            overlay.style.opacity = '1';
        }, 10);
        buttonIcon.classList.remove('bi-whatsapp');
        buttonIcon.classList.add('bi-x');
    }
});

overlay.addEventListener('click', () => {
    supportMenu.style.opacity = '0';
    overlay.style.opacity = '0';
    setTimeout(() => {
        supportMenu.classList.remove('d-flex');
        supportMenu.classList.add('d-none');
        overlay.style.display = 'none';
    }, 300);
    buttonIcon.classList.remove('bi-x');
    buttonIcon.classList.add('bi-whatsapp');
});
