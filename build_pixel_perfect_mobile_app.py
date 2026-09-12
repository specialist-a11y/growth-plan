import re

def rewrite_tracker(filepath):
    print("Rewriting pixel perfect mobile app for:", filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update CSS to enforce dark #0A0B0E background and remove light elements
    exact_mobile_css = """
/* PIXEL PERFECT TARGET MOBILE APP CSS OVERRIDES */
html, body {
  background-color: #0A0B0E !important;
  color: #FFFFFF !important;
  margin: 0;
  padding: 0;
  width: 100vw;
  max-width: 100%;
  overflow-x: hidden !important;
}

/* Mobile Screen Viewport (<= 768px) */
@media (max-width: 768px) {
  /* Hide Desktop Layout Elements */
  #appSidebar, .sidebar-column, .controls, .tabs, .top-search-box, .hero-quote-badge {
    display: none !important;
  }

  /* Full Screen Container */
  #appMainWrapper {
    margin-left: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    background: #0A0B0E !important;
    min-height: 100vh !important;
  }

  /* Top App Header Bar */
  #appTopHeader {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    height: 60px !important;
    padding: 0 16px !important;
    background: #0A0B0E !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 100 !important;
  }

  .mobile-brand-logo {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 900 !important;
    font-size: 20px !important;
    color: #ffffff !important;
  }

  .mobile-brand-crown {
    width: 32px !important;
    height: 32px !important;
    border-radius: 10px !important;
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 18px !important;
    box-shadow: 0 2px 10px rgba(245, 158, 11, 0.4) !important;
  }

  .mobile-top-right {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
  }

  .mobile-bell-btn {
    width: 36px !important;
    height: 36px !important;
    border-radius: 50% !important;
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    position: relative !important;
    font-size: 16px !important;
  }

  .mobile-bell-badge {
    position: absolute !important;
    top: 2px !important;
    right: 2px !important;
    width: 12px !important;
    height: 12px !important;
    background: #ef4444 !important;
    color: #fff !important;
    font-size: 8px !important;
    font-weight: 900 !important;
    border-radius: 50% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
  }

  .mobile-avatar-btn {
    width: 36px !important;
    height: 36px !important;
    border-radius: 50% !important;
    background: rgba(255, 255, 255, 0.15) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    color: #fff !important;
    font-weight: 900 !important;
    font-size: 13px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
  }

  /* Page Content Container */
  .page-container-grid {
    padding: 12px !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 12px !important;
    width: 100% !important;
    padding-bottom: 80px !important;
  }

  /* Hero Card Mobile Rebuild */
  .hero {
    background: linear-gradient(135deg, rgba(15, 19, 26, 0.96) 0%, rgba(8, 11, 17, 0.92) 100%), var(--hero-bg-url, none) !important;
    background-size: cover, 70% auto !important;
    background-position: top left, right bottom !important;
    background-repeat: no-repeat, no-repeat !important;
    border-radius: 24px !important;
    padding: 24px 20px !important;
    border: 1px solid rgba(255, 55, 70, 0.3) !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6) !important;
    position: relative !important;
    overflow: hidden !important;
  }

  .hero::before {
    content: 'MORE THAN AN OUTFIT';
    position: absolute;
    top: 20px;
    right: 16px;
    font-family: 'Permanent Marker', cursive, sans-serif;
    font-size: 16px;
    color: rgba(255, 255, 255, 0.7);
    transform: rotate(8deg);
    pointer-events: none;
  }

  .hero-subtitle-tag {
    font-size: 9px !important;
    letter-spacing: 2px !important;
    color: rgba(255, 255, 255, 0.5) !important;
    margin-bottom: 8px !important;
    font-weight: 800 !important;
  }

  .hero h1 {
    font-size: 22px !important;
    line-height: 1.2 !important;
    margin: 0 0 8px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 900 !important;
  }

  .hero h1 span.highlight {
    color: #FF2D40 !important;
  }

  .hero p {
    font-size: 11px !important;
    color: rgba(255, 255, 255, 0.7) !important;
    margin: 0 0 14px !important;
    line-height: 1.35 !important;
  }

  .synced-status-pill {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    padding: 6px 12px !important;
    border-radius: 16px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 8px !important;
  }

  /* 2x2 Metric Stats Grid */
  .stats {
    display: grid !important;
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 10px !important;
    width: 100% !important;
  }

  .stat {
    background: #0F131A !important;
    border: 1px solid rgba(255, 55, 70, 0.25) !important;
    border-radius: 18px !important;
    padding: 14px 16px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4) !important;
  }

  .stat-info span {
    font-size: 10px !important;
    font-weight: 800 !important;
    color: rgba(255, 255, 255, 0.6) !important;
    text-transform: uppercase !important;
  }

  .stat-info b {
    font-family: 'Outfit', sans-serif !important;
    font-size: 26px !important;
    font-weight: 900 !important;
    color: #ffffff !important;
    margin: 2px 0 !important;
    display: block !important;
  }

  .stat-info small {
    font-size: 10px !important;
    color: rgba(255, 255, 255, 0.5) !important;
  }

  .stat-icon-graphic {
    font-size: 26px !important;
  }

  /* Full Width Open Today Red CTA Button */
  .mobile-open-today-btn {
    width: 100% !important;
    padding: 16px !important;
    border-radius: 18px !important;
    font-size: 17px !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, #FF2D40 0%, #D81B30 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 6px 24px rgba(255, 45, 64, 0.5) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    cursor: pointer !important;
    margin: 2px 0 !important;
  }

  /* 3x2 App Shortcut Grid */
  .mobile-shortcut-grid {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 10px !important;
    width: 100% !important;
  }

  .mobile-shortcut-card {
    background: #0F131A !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 18px !important;
    padding: 16px 8px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    cursor: pointer !important;
    transition: border-color 0.2s, transform 0.2s !important;
  }

  .mobile-shortcut-card:active {
    transform: scale(0.96) !important;
    border-color: #FF2D40 !important;
  }

  .mobile-shortcut-icon {
    font-size: 22px !important;
  }

  .mobile-shortcut-label {
    font-size: 11px !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    text-align: center !important;
  }

  /* Choose Your Vibe Card */
  .mobile-vibe-card {
    background: linear-gradient(135deg, rgba(255, 45, 64, 0.2) 0%, #0F131A 100%) !important;
    border: 1px solid rgba(255, 45, 64, 0.35) !important;
    border-radius: 20px !important;
    padding: 16px 20px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    cursor: pointer !important;
  }

  .mobile-vibe-left {
    display: flex !important;
    align-items: center !important;
    gap: 14px !important;
  }

  .mobile-vibe-icon-box {
    width: 44px !important;
    height: 44px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #facc15 0%, #f97316 100%) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 22px !important;
    box-shadow: 0 4px 14px rgba(250, 204, 21, 0.4) !important;
  }

  .mobile-vibe-title {
    font-weight: 900 !important;
    font-size: 15px !important;
    color: #ffffff !important;
  }

  .mobile-vibe-sub {
    font-size: 11px !important;
    color: rgba(255, 255, 255, 0.7) !important;
    margin-top: 2px !important;
  }

  /* Fixed Bottom App Nav */
  #mobileBottomNav {
    display: flex !important;
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    height: 64px !important;
    background: rgba(10, 11, 14, 0.98) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
    z-index: 200 !important;
    justify-content: space-around !important;
    align-items: center !important;
    padding-bottom: env(safe-area-inset-bottom) !important;
  }

  .mobile-nav-btn {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 2px !important;
    color: rgba(255, 255, 255, 0.5) !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    cursor: pointer !important;
    border: none !important;
    background: transparent !important;
    padding: 6px 14px !important;
    border-radius: 16px !important;
    transition: all 0.2s !important;
  }

  .mobile-nav-btn.active {
    background: rgba(255, 45, 64, 0.22) !important;
    color: #FF2D40 !important;
  }

  .mobile-nav-btn-icon {
    font-size: 18px !important;
  }
}
"""

    if 'PIXEL PERFECT TARGET MOBILE APP CSS OVERRIDES' not in html:
        html = html.replace('</head>', f'<style>\n{exact_mobile_css}\n</style>\n</head>')

    # 2. Update Top Header Bar HTML to support compact mobile brand logo & actions
    header_html = """
  <!-- Top Header Bar -->
  <div id="appTopHeader">
    <div style="display:flex; align-items:center; gap:12px;">
      <div class="mobile-brand-logo">
        <div class="mobile-brand-crown">👑</div>
        <span>1GAMMA</span>
      </div>
      <div class="top-search-box">
        <span>🔍</span>
        <input type="text" placeholder="Search routines, homework, subjects..." />
      </div>
    </div>
    
    <div class="mobile-top-right">
      <div class="mobile-bell-btn">
        <span>🔔</span>
        <div class="mobile-bell-badge">1</div>
      </div>
      <button type="button" class="icon-circle-btn" onclick="openThemeModal()" title="Choose Your Vibe" style="display:none;">🎨</button>
      <div class="user-profile-badge" onclick="openSettings()" style="cursor:pointer;">
        <div class="mobile-avatar-btn">JD</div>
        <div style="font-size:12px;">
          <div style="font-weight:800; color:#fff;">Hi there!</div>
          <div style="color:rgba(255,255,255,0.6); font-size:10px;">Keep going!</div>
        </div>
      </div>
    </div>
  </div>
"""

    if 'mobile-brand-logo' not in html:
        html = re.sub(r'<div id="appTopHeader">[\s\S]*?</div>\s*</div>', header_html, html, count=1)

    # 3. Update Fixed Bottom Mobile Nav HTML to match Image 2 Exactly
    bottom_nav_html = """
<!-- Fixed Bottom Mobile Nav -->
<div id="mobileBottomNav">
  <button type="button" class="mobile-nav-btn active" id="mbNavHome" onclick="switchMainTab('calendarPanel', this)">
    <span class="mobile-nav-btn-icon">🏠</span>
    <span>Home</span>
  </button>
  <button type="button" class="mobile-nav-btn" id="mbNavRoutine" onclick="switchMainTab('todayPanel', this)">
    <span class="mobile-nav-btn-icon">☑</span>
    <span>Routine</span>
  </button>
  <button type="button" class="mobile-nav-btn" id="mbNavGoals" onclick="switchMainTab('intentionsPanel', this)">
    <span class="mobile-nav-btn-icon">🏆</span>
    <span>Goals</span>
  </button>
  <button type="button" class="mobile-nav-btn" id="mbNavMore" onclick="switchMainTab('rewardsVaultPanel', this)">
    <span class="mobile-nav-btn-icon">•••</span>
    <span>More</span>
  </button>
</div>
"""
    if 'id="mbNavMore"' not in html:
        html = re.sub(r'<div id="mobileBottomNav">[\s\S]*?</div>', bottom_nav_html, html, count=1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Cleanly rebuilt mobile UI for:", filepath)

rewrite_tracker('/Users/katrinapayne/antigravity/Growth tracker/Teen_Growth_Tracker.html')
rewrite_tracker('/Users/katrinapayne/antigravity/Growth tracker/Customizable_Growth_Tracker.html')
