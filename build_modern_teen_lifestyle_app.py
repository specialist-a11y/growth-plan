import re
import os

def process_file(filepath):
    print("Processing file:", filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # CSS Modifications
    custom_css = """
/* MODERN TEEN LIFESTYLE APP DESIGN SYSTEM CSS */
:root {
  --sidebar-w: 260px;
  --topbar-h: 70px;
}

body {
  display: flex;
  margin: 0;
  min-height: 100vh;
  background-color: var(--theme-bg, #09090b);
  color: var(--theme-text, #ffffff);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  overflow-x: hidden;
}

/* Glassmorphism Surface Base */
.card, .hero, .panel, .modal-card, .tab, .table-card, .reward-card, .fixed-routine-card, .stat, .controls, .cat-title, .cat-box, .motivation-card, .section {
  background: var(--theme-surface, rgba(15, 23, 42, 0.85)) !important;
  border: 1px solid var(--theme-border, rgba(255, 255, 255, 0.15)) !important;
  backdrop-filter: blur(20px) !important;
  -webkit-backdrop-filter: blur(20px) !important;
  color: var(--theme-text, #ffffff) !important;
  box-shadow: 0 8px 32px var(--theme-glow, rgba(0,0,0,0.3)) !important;
}

/* Left Sidebar Navigation */
#appSidebar {
  width: var(--sidebar-w);
  background: var(--theme-surface, rgba(15, 23, 42, 0.92));
  border-right: 1px solid var(--theme-border, rgba(255, 255, 255, 0.15));
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 50;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 24px 18px;
  transition: all 0.3s ease;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.sidebar-brand-icon {
  font-size: 24px;
  background: var(--theme-btn-bg, linear-gradient(135deg, #ef4444 0%, #dc2626 100%));
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 16px var(--theme-glow, rgba(239, 68, 68, 0.4));
}

.sidebar-brand-title {
  font-family: 'Outfit', sans-serif;
  font-weight: 900;
  font-size: 20px;
  letter-spacing: -0.5px;
  color: #fff;
}

.sidebar-brand-sub {
  font-size: 11px;
  color: var(--theme-text-muted, rgba(255,255,255,0.6));
  font-weight: 600;
}

.sidebar-nav-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 14px;
  color: var(--theme-text-muted, rgba(255, 255, 255, 0.75));
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.sidebar-nav-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  transform: translateX(4px);
}

.sidebar-nav-item.active {
  background: var(--theme-btn-bg, linear-gradient(135deg, #ef4444 0%, #dc2626 100%));
  color: #ffffff !important;
  border-color: var(--theme-border, rgba(255, 255, 255, 0.3));
  box-shadow: 0 4px 18px var(--theme-glow, rgba(239, 68, 68, 0.4));
}

.sidebar-footer-artwork {
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.slogan-tag {
  font-family: 'Outfit', sans-serif;
  font-weight: 900;
  font-size: 13px;
  line-height: 1.3;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Main Content Wrapper */
#appMainWrapper {
  margin-left: var(--sidebar-w);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: calc(100% - var(--sidebar-w));
}

/* Top Header Bar */
#appTopHeader {
  height: var(--topbar-h);
  background: var(--theme-surface, rgba(15, 23, 42, 0.85));
  border-bottom: 1px solid var(--theme-border, rgba(255, 255, 255, 0.1));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 0 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 40;
}

.top-search-box {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  width: 280px;
  color: #fff;
}

.top-search-box input {
  background: transparent;
  border: none;
  color: #fff;
  outline: none;
  font-family: inherit;
  font-size: 13px;
  width: 100%;
}

.icon-circle-btn {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-circle-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.user-profile-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 6px 14px 6px 6px;
  border-radius: 24px;
}

.user-avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--theme-btn-bg, linear-gradient(135deg, #ef4444 0%, #b91c1c 100%));
  color: #fff;
  font-weight: 900;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Page Layout Container (Grid on Desktop) */
.page-container-grid {
  padding: 24px;
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
  max-width: 1440px;
  width: 100%;
  margin: 0 auto;
}

.main-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Hero Section with Theme Image Overlay */
.hero {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(30, 41, 59, 0.88) 100%), var(--hero-bg-url, none) !important;
  background-size: cover !important;
  background-position: right center !important;
  border-radius: 28px !important;
  padding: 32px !important;
  position: relative;
  overflow: hidden;
  border: 1px solid var(--theme-border, rgba(255,255,255,0.2)) !important;
}

.hero-quote-badge {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.18);
  padding: 10px 16px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 600;
  color: var(--theme-text-muted, #cbd5e1);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 14px;
}

/* Button CTA overrides */
.action.primary, .btn-primary, button.action-primary {
  background: var(--theme-btn-bg, linear-gradient(135deg, #ef4444 0%, #dc2626 100%)) !important;
  color: #ffffff !important;
  border: none !important;
  box-shadow: 0 4px 18px var(--theme-glow, rgba(239, 68, 68, 0.4)) !important;
  font-weight: 800 !important;
}

/* Unified Tab Bar */
.tabs {
  display: flex;
  gap: 8px;
  background: rgba(15, 23, 42, 0.6);
  padding: 6px;
  border-radius: 18px;
  border: 1px solid var(--theme-border, rgba(255, 255, 255, 0.12));
}

.tab {
  flex: 1;
  padding: 10px 14px;
  border-radius: 14px !important;
  border: none !important;
  background: transparent !important;
  color: var(--theme-text-muted, rgba(255,255,255,0.7)) !important;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.tab:hover {
  color: #fff !important;
  background: rgba(255, 255, 255, 0.08) !important;
}

.tab.active {
  background: var(--theme-btn-bg, linear-gradient(135deg, #ef4444 0%, #dc2626 100%)) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 16px var(--theme-glow, rgba(239,68,68,0.4)) !important;
}

/* Quick Nav Cards Grid for Mobile */
.mobile-quick-nav {
  display: none;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 14px;
}

.quick-nav-card {
  background: rgba(30, 41, 59, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 18px;
  padding: 16px 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-nav-card:hover {
  transform: translateY(-2px);
  border-color: var(--theme-primary, #ef4444);
}

/* Checklist App Style for Routine Items */
.routine-checklist-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid var(--theme-border, rgba(255, 255, 255, 0.12));
  border-radius: 18px;
  padding: 14px 18px;
  margin-bottom: 10px;
  transition: all 0.2s ease;
}

.routine-checklist-item:hover {
  background: rgba(30, 41, 59, 0.95);
  border-color: var(--theme-primary, #ef4444);
}

.routine-checklist-item.completed {
  opacity: 0.65;
  text-decoration: line-through;
}

/* Fixed Bottom Mobile Nav */
#mobileBottomNav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 66px;
  background: var(--theme-surface, rgba(15, 23, 42, 0.95));
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-top: 1px solid var(--theme-border, rgba(255, 255, 255, 0.15));
  z-index: 100;
  justify-content: space-around;
  align-items: center;
  padding-bottom: env(safe-area-inset-bottom);
}

.mobile-nav-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  background: transparent;
  padding: 6px 12px;
  transition: all 0.2s;
}

.mobile-nav-btn.active {
  color: var(--theme-primary, #ef4444);
}

.mobile-nav-btn-icon {
  font-size: 20px;
}

/* Quick Idea Chips */
.quick-idea-chip {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-block;
  margin: 4px;
}

.quick-idea-chip:hover {
  background: var(--theme-primary, #ef4444);
  border-color: var(--theme-primary, #ef4444);
  transform: translateY(-1px);
}

/* Media Queries for Mobile Responsiveness */
@media (max-width: 1024px) {
  .page-container-grid {
    grid-template-columns: 1fr;
  }
  .sidebar-column {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }
}

@media (max-width: 768px) {
  #appSidebar {
    display: none !important;
  }
  #appMainWrapper {
    margin-left: 0 !important;
    width: 100% !important;
  }
  #mobileBottomNav {
    display: flex !important;
  }
  .mobile-quick-nav {
    display: grid !important;
  }
  .page-container-grid {
    padding: 14px !important;
    padding-bottom: 80px !important;
  }
  #appTopHeader {
    padding: 0 16px !important;
  }
  .top-search-box {
    display: none !important;
  }
}
"""

    if 'MODERN TEEN LIFESTYLE APP DESIGN SYSTEM CSS' not in html:
        html = html.replace('</head>', f'<style>\n{custom_css}\n</style>\n</head>')

    # Update applyThemeTokens JS function to apply hero background image overlay!
    hero_theme_js = """
      // Update Hero Section background artwork image
      const heroElem = document.querySelector('.hero');
      if (heroElem) {
        heroElem.style.setProperty('--hero-bg-url', `url("${THEME_IMAGES[themeKey] || THEME_IMAGES['sports_car']}")`);
      }
"""
    if 'heroElem.style.setProperty' not in html:
        html = html.replace('overlayLayer.style.background = `rgba(0, 0, 0, ${opacity})`;', 'overlayLayer.style.background = `rgba(0, 0, 0, ${opacity})`;\n' + hero_theme_js)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Cleanly updated:", filepath)

process_file('/Users/katrinapayne/antigravity/Growth tracker/Teen_Growth_Tracker.html')
process_file('/Users/katrinapayne/antigravity/Growth tracker/Customizable_Growth_Tracker.html')
