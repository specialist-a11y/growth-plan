import re

def rebuild_tracker(filepath):
    print("Rebuilding exact mobile app UI for:", filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update Mobile Styles to fix overflow, card size, padding, and mobile app structure
    mobile_redesign_css = """
/* NATIVE TEEN MOBILE APP RESTRUCTURE CSS */
:root {
  --app-bg-dark: #080B11;
  --card-bg-dark: #0F131A;
  --card-elevated: #151922;
  --red-primary: #FF233F;
  --red-deep: #E51D28;
  --red-glow: rgba(255, 35, 63, 0.4);
  --border-translucent: rgba(255, 55, 70, 0.3);
  --text-main: #F5F3EE;
  --text-muted: #AAB2C0;
}

html, body {
  width: 100%;
  max-width: 100%;
  overflow-x: hidden !important;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  background-color: var(--app-bg-dark);
  color: var(--text-main);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

*, *:before, *:after {
  box-sizing: border-box;
}

/* Ensure no horizontal overflow in flex/grid children */
.page-container-grid, .main-column, .hero, .stats, .controls, .tabs, .panel, .section, div, button, input {
  max-width: 100%;
  min-width: 0;
}

/* Background overlay treatment (75% dark overlay behind content) */
#appBgOverlayLayer {
  background: rgba(8, 11, 17, 0.82) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
}

/* Desktop App Container */
#appMainWrapper {
  max-width: 1280px;
  margin: 0 auto;
}

/* Mobile Specific App Viewport Rules */
@media (max-width: 768px) {
  body {
    padding-bottom: 74px !important;
  }
  
  #appSidebar {
    display: none !important;
  }
  
  #appMainWrapper {
    margin-left: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
  }
  
  /* Compact App Header */
  #appTopHeader {
    padding: 12px 14px !important;
    height: 56px !important;
    background: rgba(8, 11, 17, 0.95) !important;
    border-bottom: 1px solid var(--border-translucent) !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 90 !important;
  }
  
  .top-search-box {
    display: none !important;
  }
  
  .top-right-actions {
    gap: 10px !important;
  }

  .user-profile-badge {
    padding: 2px !important;
    background: transparent !important;
    border: none !important;
  }

  .user-profile-badge div {
    display: none !important;
  }
  
  /* Mobile Page Container */
  .page-container-grid {
    padding: 10px !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 10px !important;
    width: 100% !important;
  }

  .sidebar-column {
    display: none !important;
  }

  .main-column {
    gap: 10px !important;
    width: 100% !important;
  }
  
  /* Hero Card Mobile Rebuild */
  .hero {
    padding: 20px 16px !important;
    border-radius: 20px !important;
    background: linear-gradient(135deg, rgba(15, 19, 26, 0.94) 0%, rgba(8, 11, 17, 0.9) 100%), var(--hero-bg-url, none) !important;
    background-size: 60% auto !important;
    background-position: right bottom !important;
    background-repeat: no-repeat !important;
    border: 1px solid var(--border-translucent) !important;
  }
  
  .hero-subtitle-tag {
    font-size: 9px !important;
    letter-spacing: 2px !important;
    margin-bottom: 6px !important;
  }

  .hero h1 {
    font-size: clamp(20px, 6vw, 24px) !important;
    line-height: 1.15 !important;
    margin-bottom: 8px !important;
    word-break: break-word !important;
  }
  
  .hero p {
    font-size: 11px !important;
    line-height: 1.3 !important;
    margin-bottom: 10px !important;
    word-break: break-word !important;
  }

  .synced-status-pill {
    padding: 4px 10px !important;
    font-size: 11px !important;
    border-radius: 14px !important;
  }

  /* 2x2 Responsive Metric Stats Grid */
  .stats {
    display: grid !important;
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 8px !important;
    width: 100% !important;
  }

  .stat {
    padding: 12px 14px !important;
    border-radius: 16px !important;
    background: var(--card-bg-dark) !important;
    border: 1px solid var(--border-translucent) !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.3) !important;
  }

  .stat-info span {
    font-size: 9px !important;
    letter-spacing: 0.5px !important;
  }

  .stat-info b {
    font-size: 22px !important;
    margin: 2px 0 !important;
  }

  .stat-info small {
    font-size: 10px !important;
  }

  .stat-icon-graphic {
    font-size: 24px !important;
  }

  /* Primary Action Button CTA */
  .mobile-open-today-btn {
    width: 100% !important;
    padding: 14px !important;
    border-radius: 16px !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, var(--red-primary) 0%, var(--red-deep) 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 6px 20px var(--red-glow) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    margin: 2px 0 !important;
    cursor: pointer !important;
  }

  /* 3x2 App Shortcut Grid */
  .mobile-shortcut-grid {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 8px !important;
    width: 100% !important;
  }

  .mobile-shortcut-card {
    background: var(--card-bg-dark) !important;
    border: 1px solid var(--border-translucent) !important;
    border-radius: 16px !important;
    padding: 14px 6px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 4px !important;
  }

  .mobile-shortcut-icon {
    font-size: 20px !important;
  }

  .mobile-shortcut-label {
    font-size: 11px !important;
    font-weight: 800 !important;
    color: #ffffff !important;
  }

  /* Choose Your Vibe Banner */
  .mobile-vibe-card {
    background: linear-gradient(135deg, rgba(255, 35, 63, 0.18) 0%, var(--card-bg-dark) 100%) !important;
    border: 1px solid var(--border-translucent) !important;
    border-radius: 18px !important;
    padding: 14px 16px !important;
  }

  /* Hide Desktop Toolbar & Controls on Mobile */
  .controls {
    display: none !important;
  }

  .tabs {
    display: none !important;
  }

  /* Fixed Bottom App Nav */
  #mobileBottomNav {
    display: flex !important;
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    height: 62px !important;
    background: rgba(8, 11, 17, 0.96) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-top: 1px solid var(--border-translucent) !important;
    z-index: 100 !important;
    justify-content: space-around !important;
    align-items: center !important;
    padding-bottom: env(safe-area-inset-bottom) !important;
  }
}
"""

    if 'NATIVE TEEN MOBILE APP RESTRUCTURE CSS' not in html:
        html = html.replace('</head>', f'<style>\n{mobile_redesign_css}\n</style>\n</head>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Rebuilt mobile UI CSS for:", filepath)

rebuild_tracker('/Users/katrinapayne/antigravity/Growth tracker/Teen_Growth_Tracker.html')
rebuild_tracker('/Users/katrinapayne/antigravity/Growth tracker/Customizable_Growth_Tracker.html')
