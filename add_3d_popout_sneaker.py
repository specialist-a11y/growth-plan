import re

def apply_popout_sneaker(filepath):
    print("Applying 3D popout sneaker to:", filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Add CSS for popout sneaker in front of UI elements
    popout_css = """
/* 3D SNEAKER POPOUT IN FRONT OF UI CARD CSS */
.hero {
  position: relative !important;
  overflow: visible !important;
  z-index: 5 !important;
}

.hero-sneaker-cutout {
  position: absolute !important;
  bottom: -24px !important;
  right: -10px !important;
  width: 320px !important;
  max-width: 50% !important;
  height: auto !important;
  z-index: 20 !important;
  pointer-events: none !important;
  filter: drop-shadow(0 14px 28px rgba(0, 0, 0, 0.85)) !important;
  object-fit: contain !important;
  transform-origin: bottom right !important;
}

@media (max-width: 768px) {
  .hero {
    overflow: visible !important;
    position: relative !important;
    margin-bottom: 16px !important;
  }

  .hero-sneaker-cutout {
    width: 220px !important;
    max-width: 62% !important;
    bottom: -16px !important;
    right: -6px !important;
    z-index: 25 !important;
    filter: drop-shadow(0 10px 22px rgba(0, 0, 0, 0.9)) !important;
  }
}
"""

    if '3D SNEAKER POPOUT IN FRONT OF UI CARD CSS' not in html:
        html = html.replace('</head>', f'<style>\n{popout_css}\n</style>\n</head>')

    # 2. Add <img id="heroSneakerCutout"> inside .hero HTML
    sneaker_img_tag = '<img id="heroSneakerCutout" class="hero-sneaker-cutout" alt="Sneaker Artwork" />'
    
    if 'heroSneakerCutout' not in html:
        # Insert image tag right before closing div of hero
        html = html.replace('</div>\n  </div>\n\n  <!-- Concept 4 Stat Cards Row -->', f'{sneaker_img_tag}\n    </div>\n  </div>\n\n  <!-- Concept 4 Stat Cards Row -->')

    # 3. Update applyThemeTokens JS function to set src on heroSneakerCutout
    old_apply_js = """      // Update Hero Section background artwork image with correct bgImgKey
      const heroElem = document.querySelector('.hero');
      if (heroElem) {
        const heroImg = (theme.bgImgKey && THEME_IMAGES[theme.bgImgKey]) ? THEME_IMAGES[theme.bgImgKey] : THEME_IMAGES['sneaker_culture'];
        heroElem.style.setProperty('--hero-bg-url', `url("${heroImg}")`);
      }"""

    new_apply_js = """      // Update Hero Section background artwork image with 3D popout sneaker
      const heroElem = document.querySelector('.hero');
      const sneakerCutout = document.getElementById('heroSneakerCutout');
      const heroImg = (theme.bgImgKey && THEME_IMAGES[theme.bgImgKey]) ? THEME_IMAGES[theme.bgImgKey] : THEME_IMAGES['sneaker_culture'];
      
      if (heroElem) {
        heroElem.style.setProperty('--hero-bg-url', `url("${heroImg}")`);
      }
      if (sneakerCutout) {
        if (heroImg && !noBg) {
          sneakerCutout.src = heroImg;
          sneakerCutout.style.display = 'block';
        } else {
          sneakerCutout.style.display = 'none';
        }
      }"""

    if old_apply_js in html:
        html = html.replace(old_apply_js, new_apply_js)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully applied 3D popout sneaker to:", filepath)

apply_popout_sneaker('/Users/katrinapayne/antigravity/Growth tracker/Teen_Growth_Tracker.html')
apply_popout_sneaker('/Users/katrinapayne/antigravity/Growth tracker/Customizable_Growth_Tracker.html')
