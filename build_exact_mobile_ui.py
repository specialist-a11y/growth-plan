import re

def update_mobile_ui(filepath):
    print("Updating mobile UI for:", filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Mobile CSS overrides
    mobile_css = """
/* EXACT MOBILE UI OVERRIDES MATCHING SCREENSHOT CONCEPT */
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
  }
  
  #appTopHeader {
    padding: 12px 16px !important;
    height: auto !important;
    background: rgba(10, 11, 14, 0.95) !important;
  }
  
  .page-container-grid {
    padding: 12px !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 14px !important;
  }
  
  .sidebar-column {
    display: none !important;
  }

  .main-column {
    gap: 14px !important;
  }
  
  /* Mobile Hero Card */
  .hero {
    padding: 24px 20px !important;
    border-radius: 24px !important;
    background-position: right bottom !important;
    background-size: 65% auto !important;
  }
  
  .hero h1 {
    font-size: 22px !important;
    line-height: 1.2 !important;
  }
  
  .hero p {
    font-size: 12px !important;
    margin-bottom: 12px !important;
  }
  
  /* Mobile 2x2 Stats Grid */
  .stats {
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 10px !important;
  }
  
  .stat {
    padding: 14px !important;
    border-radius: 18px !important;
  }
  
  .stat-info b {
    font-size: 24px !important;
  }
  
  .stat-info span {
    font-size: 10px !important;
  }

  .stat-info small {
    font-size: 10px !important;
  }
  
  /* Open Today Mobile CTA Button */
  .mobile-open-today-btn {
    width: 100% !important;
    padding: 14px !important;
    border-radius: 18px !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #FF2D40 0%, #D81B30 100%) !important;
    color: #fff !important;
    border: none !important;
    box-shadow: 0 6px 20px rgba(255, 45, 64, 0.45) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    margin: 4px 0 !important;
    cursor: pointer !important;
  }

  /* Mobile 2x3 Shortcut Nav Grid */
  .mobile-shortcut-grid {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 10px !important;
  }

  .mobile-shortcut-card {
    background: rgba(20, 24, 33, 0.85) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 18px !important;
    padding: 16px 8px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    cursor: pointer !important;
    transition: transform 0.2s, border-color 0.2s !important;
  }

  .mobile-shortcut-card:hover, .mobile-shortcut-card:active {
    transform: scale(0.97) !important;
    border-color: #FF2D40 !important;
  }

  .mobile-shortcut-icon {
    font-size: 22px !important;
  }

  .mobile-shortcut-label {
    font-size: 11px !important;
    font-weight: 800 !important;
    color: #fff !important;
    text-align: center !important;
  }

  /* Mobile Choose Your Vibe Card */
  .mobile-vibe-card {
    background: linear-gradient(135deg, rgba(255, 45, 64, 0.2) 0%, rgba(20, 24, 33, 0.9) 100%) !important;
    border: 1px solid rgba(255, 45, 64, 0.35) !important;
    border-radius: 22px !important;
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
    width: 42px !important;
    height: 42px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #facc15 0%, #f97316 100%) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 22px !important;
    box-shadow: 0 4px 12px rgba(250, 204, 21, 0.4) !important;
  }

  .mobile-vibe-title {
    font-weight: 900 !important;
    font-size: 15px !important;
    color: #fff !important;
  }

  .mobile-vibe-sub {
    font-size: 11px !important;
    color: rgba(255, 255, 255, 0.7) !important;
    margin-top: 2px !important;
  }

  /* Mobile Bottom Navigation Bar */
  #mobileBottomNav {
    display: flex !important;
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    height: 64px !important;
    background: rgba(10, 11, 14, 0.96) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
    z-index: 100 !important;
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
    background: rgba(255, 45, 64, 0.2) !important;
    color: #FF2D40 !important;
  }

  .mobile-nav-btn-icon {
    font-size: 18px !important;
  }
}
"""

    if 'EXACT MOBILE UI OVERRIDES' not in html:
        html = html.replace('</head>', f'<style>\n{mobile_css}\n</style>\n</head>')

    # Inject Mobile Shortcut Grid & Open Today Button HTML if missing
    shortcut_html = """
      <!-- Mobile Open Today Prominent Button -->
      <button class="mobile-open-today-btn" onclick="openToday()">
        <span style="font-size:20px;">＋</span> Open Today
      </button>

      <!-- Mobile 2x3 Shortcut Grid -->
      <div class="mobile-shortcut-grid">
        <div class="mobile-shortcut-card" onclick="switchMainTab('calendarPanel', this)">
          <div class="mobile-shortcut-icon">📅</div>
          <div class="mobile-shortcut-label">Calendar</div>
        </div>
        <div class="mobile-shortcut-card" onclick="switchMainTab('todayPanel', this)">
          <div class="mobile-shortcut-icon">✅</div>
          <div class="mobile-shortcut-label">Daily Routine</div>
        </div>
        <div class="mobile-shortcut-card" onclick="switchMainTab('timetablePanel', this)">
          <div class="mobile-shortcut-icon">🏫</div>
          <div class="mobile-shortcut-label">Timetable</div>
        </div>
        <div class="mobile-shortcut-card" onclick="switchMainTab('rewardsVaultPanel', this)">
          <div class="mobile-shortcut-icon">🎁</div>
          <div class="mobile-shortcut-label">Reward Vault</div>
        </div>
        <div class="mobile-shortcut-card" onclick="switchMainTab('analyticsPanel', this)">
          <div class="mobile-shortcut-icon">📊</div>
          <div class="mobile-shortcut-label">Analytics</div>
        </div>
        <div class="mobile-shortcut-card" onclick="switchMainTab('intentionsPanel', this)">
          <div class="mobile-shortcut-icon">🎯</div>
          <div class="mobile-shortcut-label">Goals</div>
        </div>
      </div>

      <!-- Mobile Choose Your Vibe Card -->
      <div class="mobile-vibe-card" onclick="openThemeModal()">
        <div class="mobile-vibe-left">
          <div class="mobile-vibe-icon-box">🎨</div>
          <div>
            <div class="mobile-vibe-title">Choose Your Vibe</div>
            <div class="mobile-vibe-sub">Make your tracker feel like you!</div>
          </div>
        </div>
        <span style="font-size:18px; font-weight:900; color:rgba(255,255,255,0.7);">›</span>
      </div>
"""

    if 'mobile-shortcut-grid' not in html:
        html = html.replace('<!-- Concept 4 Stat Cards Row -->\n  <div class="stats">', '<!-- Concept 4 Stat Cards Row -->\n  <div class="stats">')
        # Insert shortcut HTML right after stats row
        html = re.sub(r'(<div class="stats">[\s\S]*?</div>\s*</div>)', r'\1\n' + shortcut_html, html, count=1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Cleanly updated mobile UI for:", filepath)

update_mobile_ui('/Users/katrinapayne/antigravity/Growth tracker/Teen_Growth_Tracker.html')
update_mobile_ui('/Users/katrinapayne/antigravity/Growth tracker/Customizable_Growth_Tracker.html')
