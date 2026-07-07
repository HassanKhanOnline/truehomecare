/* True Homecare — restores interactions that were in the WP theme's stripped scripts.
   Loaded site-wide; every block is guarded so it no-ops on pages that lack the markup. */
(function () {
  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    // 1) "See What Our Experts Can Do for You" — Swiper slider + feature-image swap
    var expertsSlider = document.querySelector('.experts-slider');
    if (expertsSlider && typeof Swiper !== 'undefined') {
      var featureImage = document.getElementById('experts-feature-image');
      new Swiper('.experts-slider', {
        loop: true,
        speed: 600,
        slidesPerView: 4,
        spaceBetween: 10,
        navigation: { nextEl: '.experts-next', prevEl: '.experts-prev' },
        breakpoints: { 0: { slidesPerView: 1 }, 768: { slidesPerView: 3 }, 1200: { slidesPerView: 4 } },
        on: {
          slideChangeTransitionStart: function () {
            if (!featureImage) return;
            var slide = this.slides[this.activeIndex];
            var image = slide && slide.getAttribute('data-image');
            if (image) {
              featureImage.style.opacity = '0';
              setTimeout(function () {
                featureImage.src = image;
                featureImage.style.opacity = '1';
              }, 300);
            }
          },
        },
      });
    }

    // 2) Custom FAQ accordion (.faq-question -> toggle .faq-item.is-open)
    var faqButtons = document.querySelectorAll('.faq-question');
    faqButtons.forEach(function (button) {
      button.addEventListener('click', function () {
        var item = button.closest('.faq-item');
        if (!item) return;
        var isOpen = item.classList.contains('is-open');
        document.querySelectorAll('.faq-item').forEach(function (faqItem) {
          faqItem.classList.remove('is-open');
          var b = faqItem.querySelector('.faq-question');
          if (b) b.setAttribute('aria-expanded', 'false');
        });
        if (!isOpen) {
          item.classList.add('is-open');
          button.setAttribute('aria-expanded', 'true');
        }
      });
    });

    // 3) "Complementary Home Support" accordions (.care-question -> toggle .care-item.active)
    document.querySelectorAll('.care-question').forEach(function (button) {
      button.addEventListener('click', function (e) {
        e.preventDefault();
        var item = button.closest('.care-item');
        if (item) item.classList.toggle('active');
      });
    });
  });
})();
