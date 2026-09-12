import json, re

# Load Base64 URIs
with open('/Users/katrinapayne/antigravity/Growth tracker/themes/processed/theme_data_uris.json') as f:
    THEME_URIS = json.load(f)

THEME_CSS = """
/* PHOTO THEME CUSTOMIZATION SYSTEM CSS */
#appBgPhotoLayer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: -2;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  pointer-events: none;
  transition: background-image 0.4s ease-in-out, opacity 0.4s ease-in-out;
  transform-origin: center center;
}

#appBgPhotoLayer.bg-motion-active {
  animation: themeBgFloat 30s ease-in-out infinite alternate;
}

@keyframes themeBgFloat {
  0% { transform: scale(1.02) translate(0, 0); }
  50% { transform: scale(1.06) translate(-8px, -5px); }
  100% { transform: scale(1.02) translate(6px, 4px); }
}

#appBgOverlayLayer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: -1;
  pointer-events: none;
  transition: background 0.4s ease-in-out, backdrop-filter 0.4s ease-in-out;
}

:root {
  --theme-primary: #FF2D2D;
  --theme-secondary: #2D9CFF;
  --theme-accent: #C8CDD3;
  --theme-bg: #090909;
  --theme-surface: rgba(18, 18, 24, 0.84);
  --theme-text: #FFFFFF;
  --theme-text-muted: #C8CDD3;
  --theme-border: rgba(255, 45, 45, 0.35);
  --theme-glow: rgba(255, 45, 45, 0.4);
  --theme-btn-bg: linear-gradient(135deg, #FF2D2D 0%, #d91c1c 100%);
  --theme-badge-bg: #FF2D2D;
}

/* Translucent surfaces with backdrop blur */
.card, .hero, .panel, .modal-card, .tab-btn, .table-card, .reward-card, .fixed-routine-card, .stat, .controls {
  background: var(--theme-surface, rgba(30, 41, 59, 0.82)) !important;
  border: 1px solid var(--theme-border, rgba(99, 102, 241, 0.35)) !important;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  color: var(--theme-text, #ffffff);
}

body {
  background-color: var(--theme-bg, #0f172a);
  color: var(--theme-text, #ffffff);
  transition: background-color 0.4s ease-in-out, color 0.4s ease-in-out;
}

/* Theme Cards in Modal */
.theme-card-item {
  background: rgba(30, 41, 59, 0.75);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  display: flex;
  flex-direction: column;
}

.theme-card-item:hover {
  transform: translateY(-4px);
  border-color: var(--theme-primary, #3b82f6);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 0 15px var(--theme-glow, rgba(59, 130, 246, 0.3));
}

.theme-card-item.selected {
  border-color: #22c55e !important;
  box-shadow: 0 0 0 2px #22c55e, 0 12px 28px -5px rgba(34, 197, 94, 0.4) !important;
}

.theme-preview-img {
  height: 150px;
  background-size: cover;
  background-position: center;
  position: relative;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.theme-badge-tag {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 20px;
  letter-spacing: 0.5px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.theme-check-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #22c55e;
  color: #fff;
  font-size: 12px;
  font-weight: 900;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.theme-swatches {
  display: flex;
  gap: 6px;
  margin-top: 10px;
}

.color-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1.5px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s;
}

.color-dot:hover {
  transform: scale(1.25);
}
"""

THEME_MODAL_HTML = """
<div id="themeModal" class="modal">
  <div class="modal-card theme-customizer-modal" style="max-width: 980px; width: 95vw; max-height: 90vh; display: flex; flex-direction: column; padding: 0; overflow: hidden; border-radius: 24px; border: 1px solid var(--theme-border, rgba(255,255,255,0.2)); background: rgba(15, 23, 42, 0.94); backdrop-filter: blur(24px); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);">
    
    <!-- Header -->
    <div class="theme-modal-header" style="padding: 20px 24px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: space-between; background: rgba(0,0,0,0.3);">
      <div>
        <h2 style="margin: 0; font-size: 22px; font-weight: 900; letter-spacing: -0.5px; color: #ffffff;">
          ✨ Choose Your Vibe
        </h2>
        <div style="color: rgba(255,255,255,0.75); font-size: 13px; margin-top: 4px; font-weight: 500;">
          Pick a background that feels like you. Your colors will change to match.
        </div>
      </div>
      <button type="button" class="close-btn" onclick="cancelThemePreview()" style="background: rgba(255,255,255,0.1); border: none; color: #fff; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 18px; display: flex; align-items: center; justify-content: center; transition: all 0.2s;">✕</button>
    </div>

    <!-- Controls Bar -->
    <div class="theme-controls-bar" style="padding: 12px 24px; background: rgba(0,0,0,0.25); border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 14px; font-size: 12px;">
      <div style="display: flex; align-items: center; gap: 10px;">
        <span style="font-weight: 800; color: rgba(255,255,255,0.75); text-transform: uppercase; letter-spacing: 0.6px; font-size: 11px;">Photo Overlay:</span>
        <div style="display: flex; background: rgba(255,255,255,0.08); border-radius: 20px; padding: 3px;">
          <button type="button" class="intensity-btn" id="intSoft" onclick="setThemeIntensity('soft')" style="border:none; padding:4px 14px; border-radius:16px; font-size:11px; font-weight:700; cursor:pointer; color:#fff; background:transparent; transition: all 0.2s;">Soft</button>
          <button type="button" class="intensity-btn" id="intBalanced" onclick="setThemeIntensity('balanced')" style="border:none; padding:4px 14px; border-radius:16px; font-size:11px; font-weight:700; cursor:pointer; color:#fff; background:rgba(255,255,255,0.2); transition: all 0.2s;">Balanced</button>
          <button type="button" class="intensity-btn" id="intVibrant" onclick="setThemeIntensity('vibrant')" style="border:none; padding:4px 14px; border-radius:16px; font-size:11px; font-weight:700; cursor:pointer; color:#fff; background:transparent; transition: all 0.2s;">Vibrant</button>
        </div>
      </div>

      <div style="display: flex; align-items: center; gap: 18px;">
        <label style="display: flex; align-items: center; gap: 7px; cursor: pointer; color: rgba(255,255,255,0.85); font-weight: 600;">
          <input type="checkbox" id="themeMotionToggle" onchange="setThemeMotion(this.checked)" checked style="accent-color: #3b82f6; width: 16px; height: 16px; cursor: pointer;">
          <span>✨ Motion Effect</span>
        </label>
        <label style="display: flex; align-items: center; gap: 7px; cursor: pointer; color: rgba(255,255,255,0.85); font-weight: 600;">
          <input type="checkbox" id="noBgToggle" onchange="setNoBackground(this.checked)" style="accent-color: #3b82f6; width: 16px; height: 16px; cursor: pointer;">
          <span>🚫 No Photo Background</span>
        </label>
      </div>
    </div>

    <!-- Theme Grid -->
    <div style="flex: 1; overflow-y: auto; padding: 22px; max-height: 60vh;">
      <div id="themeGrid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 18px;"></div>
    </div>

    <!-- Live Preview Footer -->
    <div class="theme-modal-footer" style="padding: 16px 24px; background: rgba(0,0,0,0.45); border-top: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: space-between; gap: 12px;">
      <div style="display: flex; align-items: center; gap: 10px;">
        <div id="themePreviewBadge" style="display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; color: #fff;">
          <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #22c55e; box-shadow: 0 0 10px #22c55e;"></span>
          <span id="previewThemeNameText">Active Theme: SPORTS CAR</span>
        </div>
      </div>
      <div style="display: flex; gap: 12px;">
        <button type="button" onclick="cancelThemePreview()" style="background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2); color: #fff; padding: 10px 20px; border-radius: 12px; font-weight: 700; font-size: 13px; cursor: pointer; transition: all 0.2s;">
          Cancel
        </button>
        <button type="button" onclick="applyAndSaveTheme()" style="background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%); border: none; color: #fff; padding: 10px 26px; border-radius: 12px; font-weight: 800; font-size: 13px; cursor: pointer; box-shadow: 0 4px 16px rgba(37,99,235,0.4); transition: all 0.2s;">
          Apply Theme
        </button>
      </div>
    </div>

  </div>
</div>
"""

THEME_JS = f"""
// --- PHOTO THEME CUSTOMIZATION SYSTEM ---
function openModal(id) {{
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}}
function closeModal(id) {{
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}}

const THEME_IMAGES = {json.dumps(THEME_URIS)};

const THEMES_CONFIG = {{
  sportscar: {{
    key: 'sportscar',
    name: 'SPORTS CAR',
    tagline: 'Dark city at night • Glossy black car with electric red & blue',
    badge: '🏎️ SPORTS CAR',
    bgImgKey: 'sports_car',
    colors: ['#090909', '#FF2D2D', '#C8CDD3', '#FFFFFF', '#2D9CFF'],
    colorNames: ['Black', 'Electric Red', 'Silver', 'White', 'Electric Blue'],
    primary: '#FF2D2D',
    secondary: '#2D9CFF',
    accent: '#C8CDD3',
    bg: '#090909',
    surface: 'rgba(18, 18, 24, 0.84)',
    text: '#FFFFFF',
    textMuted: '#C8CDD3',
    border: 'rgba(255, 45, 45, 0.35)',
    glow: 'rgba(255, 45, 45, 0.4)',
    btnBg: 'linear-gradient(135deg, #FF2D2D 0%, #d91c1c 100%)',
    badgeBgColor: '#FF2D2D'
  }},
  cosmic: {{
    key: 'cosmic',
    name: 'COSMIC GALAXY',
    tagline: 'Planets, nebulae & glowing space elements',
    badge: '🌌 COSMIC GALAXY',
    bgImgKey: 'cosmic_galaxy',
    colors: ['#0B0F2D', '#8B5CF6', '#00D1FF', '#FF4ED8'],
    colorNames: ['Midnight Navy', 'Purple', 'Electric Blue', 'Pink'],
    primary: '#8B5CF6',
    secondary: '#00D1FF',
    accent: '#FF4ED8',
    bg: '#0B0F2D',
    surface: 'rgba(15, 20, 50, 0.84)',
    text: '#FFFFFF',
    textMuted: '#A78BFA',
    border: 'rgba(139, 92, 246, 0.35)',
    glow: 'rgba(0, 209, 255, 0.4)',
    btnBg: 'linear-gradient(135deg, #8B5CF6 0%, #00D1FF 100%)',
    badgeBgColor: '#8B5CF6'
  }},
  gaming: {{
    key: 'gaming',
    name: 'GAMING ZONE',
    tagline: 'RGB gaming room with restrained neon glows',
    badge: '🎮 GAMING ZONE',
    bgImgKey: 'gaming_zone',
    colors: ['#1A1A1F', '#39FF14', '#A855F7', '#00E5FF'],
    colorNames: ['Charcoal', 'Neon Green', 'Purple', 'Cyan'],
    primary: '#39FF14',
    secondary: '#A855F7',
    accent: '#00E5FF',
    bg: '#1A1A1F',
    surface: 'rgba(26, 26, 33, 0.85)',
    text: '#FFFFFF',
    textMuted: '#94A3B8',
    border: 'rgba(57, 255, 20, 0.35)',
    glow: 'rgba(57, 255, 20, 0.4)',
    btnBg: 'linear-gradient(135deg, #10b981 0%, #39FF14 100%)',
    badgeBgColor: '#10b981'
  }},
  basketball: {{
    key: 'basketball',
    name: 'STREET BASKETBALL',
    tagline: 'Urban court, basketball orange & royal blue',
    badge: '🏀 BASKETBALL',
    bgImgKey: 'street_basketball',
    colors: ['#0B0B0B', '#FF8A00', '#F5E6D3', '#2563EB'],
    colorNames: ['Black', 'Basketball Orange', 'Cream', 'Royal Blue'],
    primary: '#FF8A00',
    secondary: '#2563EB',
    accent: '#F5E6D3',
    bg: '#0B0B0B',
    surface: 'rgba(20, 20, 24, 0.85)',
    text: '#F5E6D3',
    textMuted: '#D1C7BD',
    border: 'rgba(255, 138, 0, 0.35)',
    glow: 'rgba(255, 138, 0, 0.4)',
    btnBg: 'linear-gradient(135deg, #FF8A00 0%, #e06c00 100%)',
    badgeBgColor: '#FF8A00'
  }},
  tropical: {{
    key: 'tropical',
    name: 'TROPICAL WAVE',
    tagline: 'Ocean blue, turquoise waves & sunset orange',
    badge: '🌊 TROPICAL WAVE',
    bgImgKey: 'tropical_wave',
    colors: ['#006FB7', '#00D1C1', '#FF8F3D', '#F4E2C6'],
    colorNames: ['Ocean Blue', 'Turquoise', 'Sunset Orange', 'Sand'],
    primary: '#006FB7',
    secondary: '#00D1C1',
    accent: '#FF8F3D',
    bg: '#082032',
    surface: 'rgba(10, 37, 64, 0.84)',
    text: '#FFFFFF',
    textMuted: '#F4E2C6',
    border: 'rgba(0, 209, 193, 0.35)',
    glow: 'rgba(0, 209, 193, 0.4)',
    btnBg: 'linear-gradient(135deg, #006FB7 0%, #00D1C1 100%)',
    badgeBgColor: '#006FB7'
  }},
  skate: {{
    key: 'skate',
    name: 'URBAN SKATE',
    tagline: 'Graphite, electric lime & hot pink graffiti',
    badge: '🛹 URBAN SKATE',
    bgImgKey: 'urban_skate',
    colors: ['#2E2E32', '#A3FF12', '#FF2D9B', '#FFFFFF'],
    colorNames: ['Graphite', 'Lime', 'Hot Pink', 'White'],
    primary: '#A3FF12',
    secondary: '#FF2D9B',
    accent: '#FFFFFF',
    bg: '#2E2E32',
    surface: 'rgba(38, 38, 44, 0.85)',
    text: '#FFFFFF',
    textMuted: '#CBD5E1',
    border: 'rgba(163, 255, 18, 0.35)',
    glow: 'rgba(163, 255, 18, 0.4)',
    btnBg: 'linear-gradient(135deg, #84cc16 0%, #A3FF12 100%)',
    badgeBgColor: '#84cc16'
  }},
  dreamy: {{
    key: 'dreamy',
    name: 'DREAMY AURA',
    tagline: 'Lavender clouds, baby pink & sky blue moon',
    badge: '🦋 DREAMY AURA',
    bgImgKey: 'dreamy_aura',
    colors: ['#A78BFA', '#FFB3D9', '#7DD3FC', '#FFF4E6'],
    colorNames: ['Lavender', 'Baby Pink', 'Sky Blue', 'Cream'],
    primary: '#A78BFA',
    secondary: '#FFB3D9',
    accent: '#7DD3FC',
    bg: '#1E1B4B',
    surface: 'rgba(30, 27, 75, 0.84)',
    text: '#FFF4E6',
    textMuted: '#C4B5FD',
    border: 'rgba(167, 139, 250, 0.35)',
    glow: 'rgba(255, 179, 217, 0.4)',
    btnBg: 'linear-gradient(135deg, #A78BFA 0%, #FFB3D9 100%)',
    badgeBgColor: '#A78BFA'
  }},
  sneakers: {{
    key: 'sneakers',
    name: 'SNEAKER CULTURE',
    tagline: 'Off-black, red, cream & sage streetwear',
    badge: '👟 SNEAKER CULTURE',
    bgImgKey: 'sneaker_culture',
    colors: ['#111111', '#FF2D2D', '#F5E6D3', '#92A396'],
    colorNames: ['Off Black', 'Red', 'Cream', 'Sage'],
    primary: '#FF2D2D',
    secondary: '#92A396',
    accent: '#F5E6D3',
    bg: '#111111',
    surface: 'rgba(25, 25, 28, 0.85)',
    text: '#F5E6D3',
    textMuted: '#92A396',
    border: 'rgba(255, 45, 45, 0.35)',
    glow: 'rgba(255, 45, 45, 0.4)',
    btnBg: 'linear-gradient(135deg, #dc2626 0%, #FF2D2D 100%)',
    badgeBgColor: '#dc2626'
  }},
  music: {{
    key: 'music',
    name: 'MUSIC VIBES',
    tagline: 'Studio headphones, violet, aqua & hot pink beats',
    badge: '🎧 MUSIC VIBES',
    bgImgKey: 'music_vibes',
    colors: ['#0B0B0B', '#A855F7', '#2DD4BF', '#FF2D9B', '#FFFFFF'],
    colorNames: ['Black', 'Violet', 'Aqua', 'Hot Pink', 'White'],
    primary: '#A855F7',
    secondary: '#2DD4BF',
    accent: '#FF2D9B',
    bg: '#0B0B0B',
    surface: 'rgba(20, 20, 28, 0.85)',
    text: '#FFFFFF',
    textMuted: '#C084FC',
    border: 'rgba(168, 85, 247, 0.35)',
    glow: 'rgba(45, 212, 191, 0.4)',
    btnBg: 'linear-gradient(135deg, #A855F7 0%, #2DD4BF 100%)',
    badgeBgColor: '#A855F7'
  }},
  default: {{
    key: 'default',
    name: 'CLEAN DEFAULT',
    tagline: 'Sleek dark gamer interface without photo background',
    badge: '⚙️ CLEAN DEFAULT',
    bgImgKey: null,
    colors: ['#0F172A', '#2563EB', '#3B82F6', '#0284C7', '#F8FAFC'],
    colorNames: ['Slate Dark', 'Primary Blue', 'Royal Blue', 'Sky Accent', 'White'],
    primary: '#2563eb',
    secondary: '#3b82f6',
    accent: '#0284c7',
    bg: '#0f172a',
    surface: 'rgba(30, 41, 59, 0.85)',
    text: '#f8fafc',
    textMuted: '#94a3b8',
    border: 'rgba(99, 102, 241, 0.35)',
    glow: 'rgba(59, 130, 246, 0.4)',
    btnBg: 'linear-gradient(135deg, #1e40af 0%, #2563eb 50%, #0284c7 100%)',
    badgeBgColor: '#2563eb'
  }}
}};

let savedTheme = 'sportscar';
let previewTheme = 'sportscar';
let themeIntensity = 'balanced';
let themeMotion = true;
let themeNoBg = false;

function applyThemeTokens(themeKey, intensity = themeIntensity, motion = themeMotion, noBg = themeNoBg) {{
  const theme = THEMES_CONFIG[themeKey] || THEMES_CONFIG['sportscar'];
  const root = document.documentElement;

  root.style.setProperty('--theme-primary', theme.primary);
  root.style.setProperty('--theme-secondary', theme.secondary);
  root.style.setProperty('--theme-accent', theme.accent);
  root.style.setProperty('--theme-bg', theme.bg);
  root.style.setProperty('--theme-surface', theme.surface);
  root.style.setProperty('--theme-text', theme.text);
  root.style.setProperty('--theme-text-muted', theme.textMuted);
  root.style.setProperty('--theme-border', theme.border);
  root.style.setProperty('--theme-glow', theme.glow);
  root.style.setProperty('--theme-btn-bg', theme.btnBg);
  root.style.setProperty('--theme-badge-bg', theme.badgeBgColor);

  root.style.setProperty('--primary', theme.primary);
  root.style.setProperty('--card-bg', theme.surface);
  root.style.setProperty('--card-border', theme.border);
  root.style.setProperty('--ink', theme.text);
  root.style.setProperty('--muted', theme.textMuted);
  root.style.setProperty('--primary-gradient', theme.btnBg);
  root.style.setProperty('--glow-color', theme.glow);

  document.body.className = themeKey === 'default' ? '' : `theme-${{themeKey}}`;

  const photoLayer = document.getElementById('appBgPhotoLayer');
  const overlayLayer = document.getElementById('appBgOverlayLayer');

  if (photoLayer && overlayLayer) {{
    const imgData = theme.bgImgKey && THEME_IMAGES[theme.bgImgKey] ? THEME_IMAGES[theme.bgImgKey] : null;

    if (imgData && !noBg) {{
      photoLayer.style.display = 'block';
      photoLayer.style.backgroundImage = `url('${{imgData}}')`;
      
      if (motion) {{
        photoLayer.classList.add('bg-motion-active');
      }} else {{
        photoLayer.classList.remove('bg-motion-active');
      }}

      let opacity = 0.55;
      if (intensity === 'soft') opacity = 0.72;
      if (intensity === 'vibrant') opacity = 0.38;

      overlayLayer.style.background = `rgba(0, 0, 0, ${{opacity}})`;
      overlayLayer.style.backdropFilter = 'blur(4px)';
    }} else {{
      photoLayer.style.display = 'none';
      overlayLayer.style.background = theme.bg;
      overlayLayer.style.backdropFilter = 'none';
    }}
  }}
}}

function previewThemeSelection(themeKey) {{
  previewTheme = themeKey;
  applyThemeTokens(previewTheme, themeIntensity, themeMotion, themeNoBg);
  renderThemeGrid();
  updatePreviewFooter();
}}

function updatePreviewFooter() {{
  const textElem = document.getElementById('previewThemeNameText');
  if (textElem) {{
    const t = THEMES_CONFIG[previewTheme] || THEMES_CONFIG['sportscar'];
    textElem.innerText = `Previewing: ${{t.name}}`;
  }}
}}

function saveThemeState() {{
  try {{
    localStorage.setItem('growth_tracker_theme', JSON.stringify({{
      savedTheme,
      themeIntensity,
      themeMotion,
      themeNoBg
    }}));
  }} catch(e) {{}}
}}

function loadThemeConfig() {{
  try {{
    const cfg = JSON.parse(localStorage.getItem('growth_tracker_theme'));
    if (cfg) {{
      if (cfg.savedTheme) savedTheme = cfg.savedTheme;
      if (cfg.themeIntensity) themeIntensity = cfg.themeIntensity;
      if (cfg.themeMotion !== undefined) themeMotion = cfg.themeMotion;
      if (cfg.themeNoBg !== undefined) themeNoBg = cfg.themeNoBg;
    }}
  }} catch(e) {{}}
  applyThemeTokens(savedTheme, themeIntensity, themeMotion, themeNoBg);
}}

function applyAndSaveTheme() {{
  savedTheme = previewTheme;
  applyThemeTokens(savedTheme, themeIntensity, themeMotion, themeNoBg);
  saveThemeState();
  closeModal('themeModal');
}}

function cancelThemePreview() {{
  previewTheme = savedTheme;
  applyThemeTokens(savedTheme, themeIntensity, themeMotion, themeNoBg);
  closeModal('themeModal');
}}

function setThemeIntensity(val) {{
  themeIntensity = val;
  ['intSoft', 'intBalanced', 'intVibrant'].forEach(id => {{
    const btn = document.getElementById(id);
    if (btn) btn.style.background = 'transparent';
  }});
  const activeBtn = document.getElementById(val === 'soft' ? 'intSoft' : val === 'vibrant' ? 'intVibrant' : 'intBalanced');
  if (activeBtn) activeBtn.style.background = 'rgba(255,255,255,0.2)';

  applyThemeTokens(previewTheme, themeIntensity, themeMotion, themeNoBg);
}}

function setThemeMotion(val) {{
  themeMotion = val;
  applyThemeTokens(previewTheme, themeIntensity, themeMotion, themeNoBg);
}}

function setNoBackground(val) {{
  themeNoBg = val;
  applyThemeTokens(previewTheme, themeIntensity, themeMotion, themeNoBg);
}}

function openThemeModal() {{
  previewTheme = savedTheme;
  applyThemeTokens(previewTheme, themeIntensity, themeMotion, themeNoBg);

  const motionChk = document.getElementById('themeMotionToggle');
  if (motionChk) motionChk.checked = themeMotion;
  const noBgChk = document.getElementById('noBgToggle');
  if (noBgChk) noBgChk.checked = themeNoBg;

  setThemeIntensity(themeIntensity);
  renderThemeGrid();
  updatePreviewFooter();

  openModal('themeModal');
}}

function renderThemeGrid() {{
  const grid = document.getElementById('themeGrid');
  if (!grid) return;
  grid.innerHTML = '';

  Object.values(THEMES_CONFIG).forEach(t => {{
    const isSelected = previewTheme === t.key;
    const card = document.createElement('div');
    card.className = `theme-card-item ${{isSelected ? 'selected' : ''}}`;
    card.onclick = () => previewThemeSelection(t.key);

    const imgData = t.bgImgKey && THEME_IMAGES[t.bgImgKey] ? THEME_IMAGES[t.bgImgKey] : '';
    const imgStyle = imgData ? `background-image: url('${{imgData}}');` : `background: linear-gradient(135deg, ${{t.bg}} 0%, ${{t.primary}} 100%);`;

    const swatchesHtml = t.colors.map((c, i) => `
      <div class="color-dot" style="background:${{c}}" title="${{t.colorNames[i] || c}}"></div>
    `).join('');

    card.innerHTML = `
      <div class="theme-preview-img" style="${{imgStyle}}">
        <span class="theme-badge-tag">${{t.badge}}</span>
        ${{isSelected ? '<span class="theme-check-indicator">✓</span>' : ''}}
      </div>
      <div style="padding: 14px; display: flex; flex-direction: column; flex: 1; justify-content: space-between;">
        <div>
          <div style="font-weight: 900; font-size: 15px; color: #fff; letter-spacing: -0.3px;">${{t.name}}</div>
          <div style="font-size: 12px; color: rgba(255,255,255,0.7); margin-top: 4px; font-weight: 500;">${{t.tagline}}</div>
        </div>
        <div style="margin-top: 12px; display: flex; align-items: center; justify-content: space-between;">
          <div class="theme-swatches">${{swatchesHtml}}</div>
          <button type="button" onclick="event.stopPropagation(); previewThemeSelection('${{t.key}}');" style="background: ${{isSelected ? 'rgba(34,197,94,0.2)' : 'rgba(255,255,255,0.1)'}}; border: 1px solid ${{isSelected ? '#22c55e' : 'rgba(255,255,255,0.2)'}}; color: ${{isSelected ? '#22c55e' : '#fff'}}; padding: 5px 12px; border-radius: 10px; font-size: 11px; font-weight: 800; cursor: pointer; transition: all 0.2s;">
            ${{isSelected ? 'Previewing' : 'Preview'}}
          </button>
        </div>
      </div>
    `;
    grid.appendChild(card);
  }});
}}
"""

def process_file(filepath):
    print("Processing:", filepath)
    with open(filepath, 'r') as f:
        content = f.read()

    # 1. Background Layers
    if '<div id="appBgPhotoLayer"></div>' not in content:
        content = content.replace('<body>', '<body>\n<div id="appBgPhotoLayer"></div>\n<div id="appBgOverlayLayer"></div>')

    # 2. CSS before </head>
    if '#appBgPhotoLayer' not in content:
        content = content.replace('</head>', f'<style>\n{THEME_CSS}\n</style>\n</head>')

    # 3. Add Theme Button to Controls bar
    if 'openThemeModal()' not in content:
        btn_target = '<button class="action primary" onclick="openToday()">⭐ Open Today</button>'
        btn_replacement = '<button class="action primary" onclick="openToday()">⭐ Open Today</button>\n    <button class="action ghost" onclick="openThemeModal()" style="font-weight: 800; border-color: rgba(255,255,255,0.3);">🎨 Choose Your Vibe</button>'
        content = content.replace(btn_target, btn_replacement)

    # 4. Insert Modal HTML before </body>
    if '<div id="themeModal"' not in content:
        content = content.replace('</body>', f'{THEME_MODAL_HTML}\n</body>')

    # 5. Inject Theme JS before initial execution
    if '// --- PHOTO THEME CUSTOMIZATION SYSTEM ---' not in content:
        init_target = 'monthState = loadLocal(currentMonth);'
        init_replacement = f'{THEME_JS}\n\nloadThemeConfig();\nmonthState = loadLocal(currentMonth);'
        content = content.replace(init_target, init_replacement)

    with open(filepath, 'w') as f:
        f.write(content)
    print("Successfully processed:", filepath)

process_file('/Users/katrinapayne/antigravity/Growth tracker/Teen_Growth_Tracker.html')
process_file('/Users/katrinapayne/antigravity/Growth tracker/Customizable_Growth_Tracker.html')
