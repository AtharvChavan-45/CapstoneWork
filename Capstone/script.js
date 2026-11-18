document.addEventListener('DOMContentLoaded', () => {
    let currentSlide = 0;
    const slides = document.querySelectorAll('.slide');
    const totalSlides = slides.length;
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const autoplayBtn = document.getElementById('autoplay-btn');
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    const indexBtn = document.getElementById('index-btn');
    const sidebar = document.getElementById('sidebar');
    const sidebarClose = document.getElementById('sidebar-close');
    const sidebarMenu = document.getElementById('sidebar-menu');
    const curSlideText = document.getElementById('cur-slide');
    const totalSlidesText = document.getElementById('total-slides');

    let autoplayInterval = null;
    const autoplayDelay = 10000; // 10 seconds per slide

    // Update Slide count
    totalSlidesText.textContent = totalSlides;

    // Build Sidebar Menu items dynamically
    slides.forEach((slide, idx) => {
        const titleEl = slide.querySelector('.slide-header h2') || slide.querySelector('.title-header') || slide.querySelector('h1') || slide.querySelector('h2');
        let titleText = titleEl ? titleEl.textContent : `Slide ${idx + 1}`;
        titleText = titleText.replace(/\bStage\s*\d*\b/gi, '');
        titleText = titleText.replace(/[0-9✓→📊\u2713\u2192\u2013\u2014\-\.\:]+/g, '');
        titleText = titleText.replace(/\s+/g, ' ').trim();
        const menuItem = document.createElement('button');
        menuItem.className = `menu-item ${idx === 0 ? 'active' : ''}`;
        menuItem.innerHTML = `
            <span class="menu-item-num">${String(idx + 1).padStart(2, '0')}</span>
            <span class="menu-item-text">${titleText}</span>
        `;
        menuItem.addEventListener('click', () => {
            goToSlide(idx);
            closeSidebar();
        });
        sidebarMenu.appendChild(menuItem);
    });

    const menuItems = document.querySelectorAll('.menu-item');

    // Slide navigation function
    function goToSlide(index) {
        // Range check
        if (index < 0) index = 0;
        if (index >= totalSlides) index = totalSlides - 1;

        // Remove active class from old slide and menu item
        slides[currentSlide].classList.remove('active');
        menuItems[currentSlide].classList.remove('active');

        // Update current index
        currentSlide = index;

        // Add active class to new slide and menu item
        slides[currentSlide].classList.add('active');
        menuItems[currentSlide].classList.add('active');

        // Update navigation text
        curSlideText.textContent = currentSlide + 1;

        // Handle button states
        prevBtn.style.opacity = currentSlide === 0 ? '0.4' : '1';
        prevBtn.style.pointerEvents = currentSlide === 0 ? 'none' : 'auto';
        nextBtn.style.opacity = currentSlide === totalSlides - 1 ? '0.4' : '1';
        nextBtn.style.pointerEvents = currentSlide === totalSlides - 1 ? 'none' : 'auto';

        // Scroll slide body to top when shifting slide
        const activeSlideBody = slides[currentSlide].querySelector('.slide-body');
        if (activeSlideBody) {
            activeSlideBody.scrollTop = 0;
        }
    }

    // Next / Prev button event listeners
    prevBtn.addEventListener('click', () => {
        stopAutoplay();
        goToSlide(currentSlide - 1);
    });

    nextBtn.addEventListener('click', () => {
        stopAutoplay();
        goToSlide(currentSlide + 1);
    });

    // Keyboard Navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
            e.preventDefault();
            stopAutoplay();
            goToSlide(currentSlide + 1);
        } else if (e.key === 'ArrowLeft' || e.key === 'Backspace' || e.key === 'PageUp') {
            e.preventDefault();
            stopAutoplay();
            goToSlide(currentSlide - 1);
        } else if (e.key === 'Home') {
            e.preventDefault();
            stopAutoplay();
            goToSlide(0);
        } else if (e.key === 'End') {
            e.preventDefault();
            stopAutoplay();
            goToSlide(totalSlides - 1);
        } else if (e.key === 'Escape') {
            closeSidebar();
        }
    });

    // Sidebar Toggler
    indexBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    sidebarClose.addEventListener('click', closeSidebar);

    function closeSidebar() {
        sidebar.classList.remove('open');
    }

    // Close sidebar clicking outside
    document.addEventListener('click', (e) => {
        if (!sidebar.contains(e.target) && e.target !== indexBtn && !indexBtn.contains(e.target)) {
            closeSidebar();
        }
    });

    // Autoplay Controller
    function startAutoplay() {
        autoplayInterval = setInterval(() => {
            if (currentSlide < totalSlides - 1) {
                goToSlide(currentSlide + 1);
            } else {
                goToSlide(0);
            }
        }, autoplayDelay);
        autoplayBtn.classList.add('active-btn');
        autoplayBtn.innerHTML = `⚙️ Autoplay ON`;
    }

    function stopAutoplay() {
        if (autoplayInterval) {
            clearInterval(autoplayInterval);
            autoplayInterval = null;
            autoplayBtn.classList.remove('active-btn');
            autoplayBtn.innerHTML = `⚙️ Autoplay`;
        }
    }

    autoplayBtn.addEventListener('click', () => {
        if (autoplayInterval) {
            stopAutoplay();
        } else {
            startAutoplay();
        }
    });

    // Fullscreen Toggler
    fullscreenBtn.addEventListener('click', () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.error(`Error enabling fullscreen: ${err.message}`);
            });
            fullscreenBtn.innerHTML = `📺 Windowed`;
        } else {
            document.exitFullscreen();
            fullscreenBtn.innerHTML = `📺 Full Screen`;
        }
    });

    // Update button text on escape fullscreen
    document.addEventListener('fullscreenchange', () => {
        if (!document.fullscreenElement) {
            fullscreenBtn.innerHTML = `📺 Full Screen`;
        }
    });

    // Custom functions for diagram overlays
    window.toggleArchitectureDiagram = function(id) {
        const overlay = document.getElementById(id);
        if (overlay) {
            overlay.classList.toggle('show');
            const btn = document.querySelector(`.diagram-toggle-btn[onclick*="${id}"]`);
            if (overlay.classList.contains('show')) {
                btn.textContent = '❌ Close Diagram';
            } else {
                btn.textContent = id.includes('drawio') ? '👁️ View Draw.io Diagram' : '👁️ View Flowchart Image';
            }
        }
    };

    // Initialize first slide state
    goToSlide(0);
});
