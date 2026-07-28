/* True Homecare — restores interactions that were in the WP theme's stripped scripts.
   Loaded site-wide; every block is guarded so it no-ops on pages that lack the markup. */
(function () {
  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    // 0) Service pages: swap section order so the "What Is ..." feature-intro
    //    section sits ABOVE the "See What Our Experts..." slider section (one step
    //    up). They are siblings in the same wrapper. Idempotent — only moves when
    //    feature-intro currently follows experts. Runs before Swiper init below.
    var featureIntro = document.querySelector('.feature-intro-section');
    var expertsSection = document.querySelector('.experts-section');
    if (
      featureIntro &&
      expertsSection &&
      featureIntro.parentElement === expertsSection.parentElement &&
      expertsSection.compareDocumentPosition(featureIntro) & Node.DOCUMENT_POSITION_FOLLOWING
    ) {
      expertsSection.parentElement.insertBefore(featureIntro, expertsSection);
    }

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

    // 4) Active menu highlighting for the mirrored WP header (#main-menu).
    //    The mirrored markup is static and shared across every page, so it never
    //    carries the `current-menu-item` / `current-menu-parent` classes the theme
    //    CSS styles orange (#c4501f). Derive them from the current URL instead so
    //    the right item — and its parent dropdown — highlights on every page.
    var mainMenu = document.querySelector('#main-menu');
    if (mainMenu) {
      // Strip hash/query and any trailing slash so "/services/",
      // "/services" and "/services/personal-care/" compare cleanly.
      var normalize = function (path) {
        if (!path) return '';
        try { path = new URL(path, window.location.origin).pathname; } catch (e) {}
        path = path.split('#')[0].split('?')[0];
        if (path.length > 1 && path.charAt(path.length - 1) === '/') path = path.slice(0, -1);
        return path || '/';
      };
      var current = normalize(window.location.pathname);
      var isMatch = function (href) {
        if (!href || href === '#') return false;
        var h = normalize(href);
        if (h === '/') return current === '/';            // home only matches exactly
        return current === h || current.indexOf(h + '/') === 0; // self or nested route
      };

      // Clear any frozen state captured in the static markup.
      mainMenu
        .querySelectorAll('.current-menu-item, .current-menu-parent, .current-menu-ancestor')
        .forEach(function (li) {
          li.classList.remove('current-menu-item', 'current-menu-parent', 'current-menu-ancestor');
        });

      // Pick the most specific (longest) matching menu link. Only real menu
      // items — not the "Get a Free Quote" button or phone link.
      var best = null;
      var bestLen = -1;
      mainMenu.querySelectorAll('li.menu-item > a[href]').forEach(function (a) {
        var href = a.getAttribute('href');
        if (!isMatch(href)) return;
        var len = normalize(href).length;
        if (len > bestLen) { bestLen = len; best = a; }
      });

      if (best) {
        var li = best.closest('li');
        if (li) {
          li.classList.add('current-menu-item');
          // Walk up to the top-level <li> so a dropdown child also lights up
          // its parent ("Services" turns orange on any service page).
          var topLevel = li;
          while (topLevel.parentElement && topLevel.parentElement !== mainMenu) {
            var parentLi = topLevel.parentElement.closest('li');
            if (!parentLi || parentLi === topLevel) break;
            topLevel = parentLi;
          }
          if (topLevel !== li) topLevel.classList.add('current-menu-parent');
        }
      }
    }

    // 5) Service-page reviews widget (Trustindex). The mirror stripped the loader
    //    <script> out of the service-page ".reviews-wrap", leaving it empty, so the
    //    Google-reviews widget the live site shows never renders. Re-inject the same
    //    loader (widget id 216e72c55b53491403760892d86) so it renders identically.
    //    Guarded to the empty .reviews-wrap only (the homepage uses different markup).
    var reviewsWrap = document.querySelector('.reviews-wrap');
    if (
      reviewsWrap &&
      reviewsWrap.children.length === 0 &&
      !reviewsWrap.getAttribute('data-thc-reviews-loaded')
    ) {
      reviewsWrap.setAttribute('data-thc-reviews-loaded', '1');
      var tiScript = document.createElement('script');
      tiScript.src = 'https://cdn.trustindex.io/loader.js?216e72c55b53491403760892d86';
      tiScript.async = true;
      tiScript.defer = true;
      reviewsWrap.appendChild(tiScript);
    }

    // 6) Location-page reviews widget (Trustindex). The loader <script> IS present
    //    in the mirror markup, but Astro's set:html doesn't execute injected scripts,
    //    so the widget stays blank. Re-create it (using its own src) so it executes.
    //    Guarded: only when the widget hasn't already rendered.
    var locReviews = document.querySelector('.location-block-testimonials-trf');
    if (
      locReviews &&
      !locReviews.querySelector('.ti-widget') &&
      !locReviews.getAttribute('data-thc-reviews-loaded')
    ) {
      locReviews.setAttribute('data-thc-reviews-loaded', '1');
      // The Trustindex loader renders a widget at EACH of its own <script> tags.
      // The mirror already contains one (inert) copy; remove all inert copies first
      // and grab the loader src, then inject exactly one so only a single widget
      // renders (matching the live page, which shows one).
      var inertScripts = locReviews.querySelectorAll('script[src*="cdn.trustindex.io"]');
      var loaderSrc =
        inertScripts.length
          ? inertScripts[0].src || inertScripts[0].getAttribute('src')
          : 'https://cdn.trustindex.io/loader.js?216e72c55b53491403760892d86';
      for (var k = 0; k < inertScripts.length; k++) {
        if (inertScripts[k].parentNode) inertScripts[k].parentNode.removeChild(inertScripts[k]);
      }
      var locScript = document.createElement('script');
      locScript.src = loaderSrc;
      locScript.async = true;
      locScript.defer = true;
      locReviews.appendChild(locScript);
    }

    // 7) Location-page image gallery ("See the heart behind the care we provide").
    //    The mirror ships the Slick markup + slick.css, but jQuery/Slick and the init
    //    call were stripped, so it fell back to a static two-row grid. It is a synced
    //    main+thumbnail gallery (like live): the "content" slider shows one large image,
    //    the "thumb" slider shows four thumbnails, linked via asNavFor. jQuery +
    //    slick.min.js are loaded before this file.
    if (window.jQuery && window.jQuery.fn && window.jQuery.fn.slick) {
      var $content = window.jQuery('.block-image-gallery-slider-content');
      var $thumb = window.jQuery('.block-image-gallery-slider-thumb');
      if ($content.length && $thumb.length && !$content.hasClass('slick-initialized')) {
        $content.slick({
          slidesToShow: 1,
          slidesToScroll: 1,
          arrows: true,
          dots: false,
          infinite: false,
          speed: 500,
          asNavFor: '.block-image-gallery-slider-thumb'
        });
        $thumb.slick({
          slidesToShow: 4,
          slidesToScroll: 1,
          arrows: true,
          dots: false,
          infinite: false,
          focusOnSelect: true,
          asNavFor: '.block-image-gallery-slider-content',
          responsive: [
            { breakpoint: 992, settings: { slidesToShow: 4 } },
            { breakpoint: 768, settings: { slidesToShow: 3 } },
            { breakpoint: 480, settings: { slidesToShow: 2 } }
          ]
        });
      }
    }
  });
})();
