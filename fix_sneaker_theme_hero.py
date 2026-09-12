import re

def fix_tracker(filepath):
    print("Fixing Sneaker Theme Hero rendering for:", filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Set default savedTheme and previewTheme to 'sneakers'
    html = html.replace("let savedTheme = 'sportscar';", "let savedTheme = 'sneakers';")
    html = html.replace("let previewTheme = 'sportscar';", "let previewTheme = 'sneakers';")

    # 2. Fix image key lookup in applyThemeTokens JS function
    old_hero_js = """      // Update Hero Section background artwork image
      const heroElem = document.querySelector('.hero');
      if (heroElem) {
        heroElem.style.setProperty('--hero-bg-url', `url("${THEME_IMAGES[themeKey] || THEME_IMAGES['sports_car']}")`);
      }"""

    new_hero_js = """      // Update Hero Section background artwork image with correct bgImgKey
      const heroElem = document.querySelector('.hero');
      if (heroElem) {
        const heroImg = (theme.bgImgKey && THEME_IMAGES[theme.bgImgKey]) ? THEME_IMAGES[theme.bgImgKey] : THEME_IMAGES['sneaker_culture'];
        heroElem.style.setProperty('--hero-bg-url', `url("${heroImg}")`);
      }"""

    if 'heroElem.style.setProperty' in html:
        html = html.replace(old_hero_js, new_hero_js)

    # 3. CSS for Mobile (Image 1) & Desktop (Image 2) Hero Section
    hero_css_override = """
/* SNEAKER THEME HERO SECTION SPECIFIC OVERRIDES */
.hero {
  background: linear-gradient(90deg, rgba(10, 12, 17, 0.96) 0%, rgba(13, 16, 23, 0.90) 50%, rgba(15, 20, 28, 0.4) 100%), var(--hero-bg-url, none) !important;
  background-size: cover, auto 100% !important;
  background-position: left center, right center !important;
  background-repeat: no-repeat, no-repeat !important;
  position: relative !important;
  overflow: hidden !important;
}

.hero::before {
  content: 'MORE THAN AN OUTFIT';
  position: absolute;
  top: 24px;
  right: 28px;
  font-family: 'Permanent Marker', cursive, sans-serif;
  font-size: 24px;
  line-height: 1.1;
  color: rgba(255, 255, 255, 0.7);
  transform: rotate(8deg);
  pointer-events: none;
  text-shadow: 0 2px 8px rgba(0,0,0,0.8);
}

@media (max-width: 768px) {
  .hero {
    background: linear-gradient(180deg, rgba(10, 12, 17, 0.94) 0%, rgba(13, 16, 23, 0.85) 60%, rgba(15, 20, 28, 0.4) 100%), var(--hero-bg-url, none) !important;
    background-size: cover, 75% auto !important;
    background-position: top left, right bottom !important;
    background-repeat: no-repeat, no-repeat !important;
    padding: 24px 18px !important;
    min-height: 230px !important;
  }

  .hero::before {
    font-size: 16px !important;
    top: 18px !important;
    right: 14px !important;
  }
}
"""

    if 'SNEAKER THEME HERO SECTION SPECIFIC OVERRIDES' not in html:
        html = html.replace('</head>', f'<style>\n{hero_css_override}\n</style>\n</head>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Cleanly updated Sneaker theme hero for:", filepath)

fix_tracker('/Users/katrinapayne/antigravity/Growth tracker/Teen_Growth_Tracker.html')
fix_tracker('/Users/katrinapayne/antigravity/Growth tracker/Customizable_Growth_Tracker.html')
