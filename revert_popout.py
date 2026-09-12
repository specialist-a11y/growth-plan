import re

def revert_tracker(filepath):
    print("Reverting 3D popout changes for:", filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Remove 3D popout CSS block
    popout_css_pattern = r'/\* 3D SNEAKER POPOUT IN FRONT OF UI CARD CSS \*/[\s\S]*?}\n}'
    html = re.sub(popout_css_pattern, '', html)

    # 2. Remove <img id="heroSneakerCutout"> tag
    html = html.replace('<img id="heroSneakerCutout" class="hero-sneaker-cutout" alt="Sneaker Artwork" />\n', '')
    html = html.replace('<img id="heroSneakerCutout" class="hero-sneaker-cutout" alt="Sneaker Artwork" />', '')

    # 3. Restore previous applyThemeTokens JS function
    old_apply_js = """      // Update Hero Section background artwork image with 3D popout sneaker
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

    restored_apply_js = """      // Update Hero Section background artwork image
      const heroElem = document.querySelector('.hero');
      if (heroElem) {
        const heroImg = (theme.bgImgKey && THEME_IMAGES[theme.bgImgKey]) ? THEME_IMAGES[theme.bgImgKey] : THEME_IMAGES['sneaker_culture'];
        heroElem.style.setProperty('--hero-bg-url', `url("${heroImg}")`);
      }"""

    if old_apply_js in html:
        html = html.replace(old_apply_js, restored_apply_js)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Reverted successfully for:", filepath)

revert_tracker('/Users/katrinapayne/antigravity/Growth tracker/Teen_Growth_Tracker.html')
revert_tracker('/Users/katrinapayne/antigravity/Growth tracker/Customizable_Growth_Tracker.html')
