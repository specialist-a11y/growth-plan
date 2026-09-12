import re
import os

def update_tracker(filepath):
    print("Updating file to exact concept design:", filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Add Google Fonts (Permanent Marker for Graffiti Slogans, Outfit, Inter)
    fonts_link = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;700;800;900&family=Permanent+Marker&display=swap" rel="stylesheet">'
    if 'Permanent+Marker' not in html:
        html = html.replace('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800;900&display=swap" rel="stylesheet">', fonts_link)

    # 2. Add Exact Concept CSS
    exact_css = """
/* EXACT CONCEPT DESIGN SYSTEM CSS */
:root {
  --app-bg: #0A0B0E;
  --sidebar-w: 260px;
  --topbar-h: 70px;
  --theme-primary: #FF2D40;
  --theme-btn-bg: linear-gradient(135deg, #FF2D40 0%, #D81B30 100%);
  --theme-glow: rgba(255, 45, 64, 0.45);
}

body {
  background-color: var(--app-bg) !important;
  color: #FFFFFF !important;
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* Graffiti Typography */
.graffiti-text {
  font-family: 'Permanent Marker', cursive, sans-serif;
  color: rgba(255, 255, 255, 0.25);
  text-transform: uppercase;
  letter-spacing: 1px;
  pointer-events: none;
  user-select: none;
}

/* Sidebar Exact Concept Styling */
#appSidebar {
  width: var(--sidebar-w);
  background: rgba(13, 16, 22, 0.95) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
  backdrop-filter: blur(24px) !important;
}

.sidebar-brand-icon {
  background: linear-gradient(135deg, #FF2D40 0%, #C41225 100%) !important;
  box-shadow: 0 4px 16px rgba(255, 45, 64, 0.5) !important;
}

.sidebar-nav-item.active {
  background: linear-gradient(135deg, #FF2D40 0%, #D81B30 100%) !important;
  color: #FFFFFF !important;
  box-shadow: 0 4px 18px rgba(255, 45, 64, 0.45) !important;
  border-radius: 12px !important;
}

/* Top Bar Exact Concept Styling */
#appTopHeader {
  background: rgba(13, 16, 22, 0.9) !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
}

.top-search-box {
  background: rgba(255, 255, 255, 0.06) !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  border-radius: 20px !important;
  width: 380px !important;
}

/* Hero Section Exact Concept Styling */
.hero {
  background: linear-gradient(135deg, rgba(13, 16, 22, 0.94) 0%, rgba(20, 24, 33, 0.9) 100%), var(--hero-bg-url, none) !important;
  background-size: cover !important;
  background-position: right center !important;
  border-radius: 24px !important;
  padding: 36px 40px !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5) !important;
}

.hero-subtitle-tag {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 2.5px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  margin-bottom: 10px;
}

.hero h1 {
  font-family: 'Outfit', sans-serif !important;
  font-weight: 900 !important;
  font-size: clamp(28px, 3.5vw, 40px) !important;
  line-height: 1.15 !important;
  margin: 0 0 10px !important;
}

.hero h1 span.highlight {
  color: #FF2D40;
}

.synced-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  color: #fff;

}

.synced-status-pill .dot {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
  box-shadow: 0 0 8px #22c55e;
}

/* Stat Cards Exact Concept */
.stats {
  display: grid !important;
  grid-template-columns: repeat(4, 1fr) !important;
  gap: 16px !important;
}

.stat {
  background: rgba(20, 24, 33, 0.85) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 20px !important;
  padding: 20px !important;
  position: relative !important;
  overflow: hidden !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
}

.stat-info span {
  font-size: 11px !important;
  font-weight: 800 !important;
  letter-spacing: 0.8px !important;
  text-transform: uppercase !important;
  color: rgba(255, 255, 255, 0.6) !important;
}

.stat-info b {
  font-family: 'Outfit', sans-serif !important;
  font-size: 32px !important;
  font-weight: 900 !important;
  color: #fff !important;
  margin: 4px 0 2px !important;
  display: block !important;
}

.stat-info small {
  font-size: 12px !important;
  color: rgba(255, 255, 255, 0.5) !important;
}

.stat-icon-graphic {
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Compact Control Bar Exact Concept */
.controls {
  background: rgba(20, 24, 33, 0.8) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 20px !important;
  padding: 10px 14px !important;
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  flex-wrap: wrap !important;
}

.controls .action.primary {
  background: linear-gradient(135deg, #FF2D40 0%, #D81B30 100%) !important;
  box-shadow: 0 4px 20px rgba(255, 45, 64, 0.45) !important;
  border-radius: 14px !important;
  padding: 10px 22px !important;
  font-weight: 800 !important;
  border: none !important;
}

.controls .action.ghost {
  background: rgba(255, 255, 255, 0.06) !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  border-radius: 14px !important;
  color: #fff !important;
  font-weight: 700 !important;
  font-size: 13px !important;
  padding: 10px 16px !important;
}

.controls .action.ghost:hover {
  background: rgba(255, 255, 255, 0.15) !important;
}

/* Tabs Bar Exact Concept */
.tabs {
  background: rgba(13, 16, 22, 0.7) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 18px !important;
  padding: 6px !important;
}

.tab.active {
  background: linear-gradient(135deg, #FF2D40 0%, #D81B30 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 18px rgba(255, 45, 64, 0.45) !important;
  border-radius: 14px !important;
}

/* Left & Right 2-Column Main Section */
.main-column .section {
  position: relative;
  overflow: hidden;
  border-radius: 24px !important;
  padding: 28px !important;
  background: rgba(20, 24, 33, 0.85) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.main-column .section::after {
  content: 'BETTER HABITS BIGGER TOMORROWS';
  position: absolute;
  bottom: 12px;
  right: 20px;
  font-family: 'Permanent Marker', cursive, sans-serif;
  font-size: 18px;
  color: rgba(255, 255, 255, 0.08);
  pointer-events: none;
}

/* Motivation & Focus Cards */
.motivation-card {
  position: relative;
  overflow: hidden;
  border-radius: 24px !important;
  padding: 24px !important;
  background: linear-gradient(135deg, rgba(20, 24, 33, 0.95) 0%, rgba(13, 16, 22, 0.95) 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
}

.motivation-card::after {
  content: 'GOOD HABITS WIN';
  position: absolute;
  bottom: 8px;
  right: 14px;
  font-family: 'Permanent Marker', cursive, sans-serif;
  font-size: 20px;
  color: rgba(255, 45, 64, 0.3);
  transform: rotate(-6deg);
  pointer-events: none;
}

.focus-card {
  position: relative;
  overflow: hidden;
  border-radius: 24px !important;
  padding: 24px !important;
  background: rgba(20, 24, 33, 0.85) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.focus-card::after {
  content: 'DISCIPLINE TODAY FREEDOM TOMORROW';
  position: absolute;
  bottom: 10px;
  right: 14px;
  font-family: 'Permanent Marker', cursive, sans-serif;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.12);
  transform: rotate(-3deg);
  pointer-events: none;
}
"""

    if 'EXACT CONCEPT DESIGN SYSTEM CSS' not in html:
        html = html.replace('</head>', f'<style>\n{exact_css}\n</style>\n</head>')

    # 3. Update Hero Section HTML markup to match concept exactly
    concept_hero_html = """
  <!-- Concept Hero Section -->
  <div class="hero">
    <div style="display:flex; justify-content:space-between; align-items:flex-start; position:relative; z-index:2;">
      <div style="max-width:620px;">
        <div class="hero-subtitle-tag">REPEAT • LEARN • IMPROVE • GROW</div>
        <h1>⚡ 12-Year-Old Daily <span class="highlight">Growth & Routine</span> Tracker</h1>
        <p style="font-size:14px; color:rgba(255,255,255,0.7); margin:0 0 16px;">Queen's College • Class 1GAMMA (Mr. R. Beckles) • School Prep • Chores & Homework</p>
        <div class="synced-status-pill">
          <span class="dot"></span>
          <span>All synced</span>
          <span style="opacity:0.6; font-weight:500;">Last synced today at 9:41 AM ☁️</span>
        </div>
      </div>
    </div>
  </div>
"""

    # Replace existing hero HTML
    old_hero_pattern = r'<div class="hero">.*?</div>\s*</div>'
    if re.search(r'<div class="hero">', html):
        html = re.sub(r'<div class="hero">[\s\S]*?</div>\s*</div>', concept_hero_html, html, count=1)

    # 4. Update Stat Cards HTML to match concept exactly
    concept_stats_html = """
  <!-- Concept 4 Stat Cards Row -->
  <div class="stats">
    <div class="stat">
      <div class="stat-info">
        <span>AVERAGE COMPLETION</span>
        <b id="avgPct">0%</b>
        <small>Keep going — you've got this!</small>
      </div>
      <div class="stat-icon-graphic">🎯</div>
    </div>
    <div class="stat">
      <div class="stat-info">
        <span>CURRENT STREAK</span>
        <b id="streakCount">1 day</b>
        <small>Nice! Keep the momentum!</small>
      </div>
      <div class="stat-icon-graphic">🔥</div>
    </div>
    <div class="stat">
      <div class="stat-info">
        <span>HOMEWORK DONE</span>
        <b id="homeworkCount">0</b>
        <small>Every task counts!</small>
      </div>
      <div class="stat-icon-graphic">📖</div>
    </div>
    <div class="stat">
      <div class="stat-info">
        <span>PERFECT DAYS</span>
        <b id="perfectDays">0</b>
        <small>Aiming for greatness!</small>
      </div>
      <div class="stat-icon-graphic">🏆</div>
    </div>
  </div>
"""

    if re.search(r'<div class="stats">', html):
        html = re.sub(r'<div class="stats">[\s\S]*?</div>\s*</div>', concept_stats_html, html, count=1)

    # 5. Update Sidebar Footer Slogan HTML
    concept_sidebar_footer = """
  <div class="sidebar-footer-artwork">
    <div class="graffiti-text" style="font-size:16px; line-height:1.2; margin-bottom:12px; color:rgba(255,255,255,0.3); transform:rotate(-4deg);">
      DISCIPLINE<br>CREATES<br><span style="color:#FF2D40;">FREEDOM</span>
    </div>
    <div style="font-family:'Outfit', sans-serif; font-size:11px; font-weight:900; color:rgba(255,255,255,0.5); text-transform:uppercase; letter-spacing:1px;">
      URBAN MINDS<br><span style="color:#FF2D40;">BRIGHTER</span> TOMORROW
    </div>
    <div style="font-size:9px; color:rgba(255,255,255,0.3); margin-top:4px; font-weight:800; letter-spacing:1.5px;">A 1GAMMA JOURNEY</div>
  </div>
"""
    if re.search(r'<div class="sidebar-footer-artwork">', html):
        html = re.sub(r'<div class="sidebar-footer-artwork">[\s\S]*?</div>\s*</div>', concept_sidebar_footer, html, count=1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Cleanly updated file to exact concept:", filepath)

update_tracker('/Users/katrinapayne/antigravity/Growth tracker/Teen_Growth_Tracker.html')
update_tracker('/Users/katrinapayne/antigravity/Growth tracker/Customizable_Growth_Tracker.html')
