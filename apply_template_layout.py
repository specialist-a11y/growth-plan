import re

TEMPLATE_CSS = """
/* DESKTOP & MOBILE APPLOCK TEMPLATE SYSTEM CSS */
:root {
  --sidebar-width: 260px;
  --topbar-height: 70px;
}

body {
  display: flex;
  min-height: 100vh;
  background-color: var(--theme-bg, #09090b);
  color: var(--theme-text, #ffffff);
  overflow-x: hidden;
}

/* Left Sidebar Navigation */
#appSidebar {
  width: var(--sidebar-width);
  background: var(--theme-surface, rgba(15, 23, 42, 0.92));
  border-right: 1px solid var(--theme-border, rgba(255, 255, 255, 0.12));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 40;
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
  margin-bottom: 28px;
}

.sidebar-brand-icon {
  font-size: 26px;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 14px rgba(239, 68, 68, 0.4);
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
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.25) 0%, rgba(220, 38, 38, 0.4) 100%);
  color: #ffffff;
  border-color: rgba(239, 68, 68, 0.5);
  box-shadow: 0 4px 16px rgba(239, 68, 68, 0.25);
}

.sidebar-nav-item-icon {
  font-size: 18px;
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
  margin-left: var(--sidebar-width);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: calc(100% - var(--sidebar-width));
}

/* Top Header Bar */
#appTopHeader {
  height: var(--topbar-height);
  background: var(--theme-surface, rgba(15, 23, 42, 0.85));
  border-bottom: 1px solid var(--theme-border, rgba(255, 255, 255, 0.1));
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  padding: 0 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 30;
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
  font-size: 13px;
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

.top-right-actions {
  display: flex;
  align-items: center;
  gap: 16px;
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
  background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
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

/* Sneaker Motivation Card */
.motivation-card {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
  border: 1px solid var(--theme-border, rgba(255, 255, 255, 0.15));
  border-radius: 24px;
  padding: 22px;
  position: relative;
  overflow: hidden;
}

.motivation-card-tag {
  font-weight: 900;
  font-size: 16px;
  color: #fff;
  margin-bottom: 8px;
}

.motivation-card-text {
  font-size: 13px;
  color: var(--theme-text-muted, rgba(255,255,255,0.7));
  line-height: 1.45;
}

/* Quick Nav Cards Grid for Mobile */
.mobile-quick-nav {
  display: none;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 14px;
}

.quick-nav-card {
  background: rgba(30, 41, 59, 0.8);
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

.quick-nav-card-icon {
  font-size: 22px;
  margin-bottom: 6px;
}

.quick-nav-card-title {
  font-size: 11px;
  font-weight: 800;
  color: #fff;
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
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid var(--theme-border, rgba(255, 255, 255, 0.12));
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
  color: #ef4444;
}

.mobile-nav-btn-icon {
  font-size: 20px;
}

/* Responsive Media Queries */
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

def update_file(filepath):
    print("Applying template layout to:", filepath)
    with open(filepath, 'r') as f:
        content = f.read()

    # 1. Add TEMPLATE_CSS before </head>
    if '/* DESKTOP & MOBILE APPLOCK TEMPLATE SYSTEM CSS */' not in content:
        content = content.replace('</head>', f'<style>\n{TEMPLATE_CSS}\n</style>\n</head>')

    # 2. Add Sidebar HTML & Top Header HTML & Right Sidebar Layout inside body
    if 'id="appSidebar"' not in content:
        sidebar_html = """
<div id="appSidebar">
  <div>
    <div class="sidebar-brand">
      <div class="sidebar-brand-icon">👑</div>
      <div>
        <div class="sidebar-brand-title">1GAMMA</div>
        <div class="sidebar-brand-sub">Grow Today. Greater Tomorrow.</div>
      </div>
    </div>
    
    <ul class="sidebar-nav-list">
      <li class="sidebar-nav-item active" onclick="switchMainTab('calendarPanel', this)">
        <span class="sidebar-nav-item-icon">🏠</span>
        <span>Dashboard</span>
      </li>
      <li class="sidebar-nav-item" onclick="switchMainTab('calendarPanel', this)">
        <span class="sidebar-nav-item-icon">📅</span>
        <span>Calendar</span>
      </li>
      <li class="sidebar-nav-item" onclick="switchMainTab('todayPanel', this)">
        <span class="sidebar-nav-item-icon">✅</span>
        <span>Daily Routine</span>
      </li>
      <li class="sidebar-nav-item" onclick="switchMainTab('timetablePanel', this)">
        <span class="sidebar-nav-item-icon">🏫</span>
        <span>1GAMMA Timetable</span>
      </li>
      <li class="sidebar-nav-item" onclick="switchMainTab('rewardsVaultPanel', this)">
        <span class="sidebar-nav-item-icon">🎁</span>
        <span>Reward Vault</span>
      </li>
      <li class="sidebar-nav-item" onclick="switchMainTab('analyticsPanel', this)">
        <span class="sidebar-nav-item-icon">📊</span>
        <span>Analytics & Trophies</span>
      </li>
      <li class="sidebar-nav-item" onclick="switchMainTab('novelsPanel', this)">
        <span class="sidebar-nav-item-icon">📖</span>
        <span>Novel & Skill Log</span>
      </li>
      <li class="sidebar-nav-item" onclick="switchMainTab('intentionsPanel', this)">
        <span class="sidebar-nav-item-icon">🎯</span>
        <span>Goals & Rewards</span>
      </li>
    </ul>
  </div>

  <div class="sidebar-footer-artwork">
    <div class="slogan-tag">URBAN MINDS<br><span style="color:#ef4444;">BRIGHTER</span> TOMORROW</div>
    <div style="font-size:10px; color:rgba(255,255,255,0.3); margin-top:8px; font-weight:800;">DISCIPLINE CREATES FREEDOM</div>
  </div>
</div>

<div id="appMainWrapper">
  <!-- Top Header Bar -->
  <div id="appTopHeader">
    <div style="display:flex; align-items:center; gap:12px;">
      <div style="font-family:'Outfit', sans-serif; font-weight:900; font-size:18px; color:#fff; display:flex; align-items:center; gap:8px;">
        <span style="color:#ef4444;">👑</span> 1GAMMA
      </div>
      <div class="top-search-box">
        <span>🔍</span>
        <input type="text" placeholder="Search routines, homework, subjects..." />
      </div>
    </div>
    
    <div class="top-right-actions">
      <button type="button" class="icon-circle-btn" onclick="openThemeModal()" title="Choose Your Vibe">🎨</button>
      <button type="button" class="icon-circle-btn" onclick="openSettings()" title="Account & Sync">🔑</button>
      <div class="user-profile-badge">
        <div class="user-avatar-circle">JD</div>
        <div style="font-size:12px;">
          <div style="font-weight:800; color:#fff;">Hi there!</div>
          <div style="color:rgba(255,255,255,0.6); font-size:10px;">Keep going!</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Main Grid Page Layout -->
  <div class="page-container-grid">
    <div class="main-column">
"""
        content = content.replace('<body>\n<div id="appBgPhotoLayer"></div>\n<div id="appBgOverlayLayer"></div>\n\n<div class="wrap">', '<body>\n<div id="appBgPhotoLayer"></div>\n<div id="appBgOverlayLayer"></div>\n' + sidebar_html)

    # 3. Add Mobile Quick Nav & Right Sidebar & Bottom Mobile Nav before </body>
    if 'id="mobileBottomNav"' not in content:
        mobile_bottom_html = """
    </div> <!-- /main-column -->

    <!-- Right Sidebar Column (Motivation & Focus Cards) -->
    <div class="sidebar-column">
      
      <!-- Sneaker Motivation Card -->
      <div class="motivation-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div class="motivation-card-tag">👟 Progress Builds Confidence</div>
          <span style="font-size:24px;">👟</span>
        </div>
        <div class="motivation-card-text" style="margin-top:6px;">
          Consistent actions today lead to amazing opportunities tomorrow. Small steps every day build big futures!
        </div>
      </div>

      <!-- This Month's Focus Card -->
      <div class="section" style="margin:0;">
        <h3 style="margin:0 0 12px; font-size:16px; font-weight:800; display:flex; align-items:center; gap:8px;">
          <span>⭐</span> This Month's Focus
        </h3>
        <div style="display:flex; flex-direction:column; gap:10px; font-size:13px; font-weight:600; color:rgba(255,255,255,0.85);">
          <label style="display:flex; align-items:center; gap:8px; cursor:pointer;"><input type="checkbox" checked style="accent-color:#ef4444;"> <span>Be consistent</span></label>
          <label style="display:flex; align-items:center; gap:8px; cursor:pointer;"><input type="checkbox" checked style="accent-color:#ef4444;"> <span>Make progress, not perfection</span></label>
          <label style="display:flex; align-items:center; gap:8px; cursor:pointer;"><input type="checkbox" style="accent-color:#ef4444;"> <span>Build the best version of you</span></label>
          <label style="display:flex; align-items:center; gap:8px; cursor:pointer;"><input type="checkbox" style="accent-color:#ef4444;"> <span>You can do this!</span></label>
        </div>
      </div>

      <!-- Choose Your Vibe Card -->
      <div class="section" onclick="openThemeModal()" style="margin:0; cursor:pointer; background:linear-gradient(135deg, rgba(239,68,68,0.2) 0%, rgba(30,41,59,0.8) 100%); border-color:rgba(239,68,68,0.4); display:flex; align-items:center; justify-content:space-between;">
        <div>
          <div style="font-weight:900; font-size:15px; color:#fff;">🎨 Choose Your Vibe</div>
          <div style="font-size:12px; color:rgba(255,255,255,0.7); margin-top:2px;">Themes, colors & styles</div>
        </div>
        <span style="font-weight:900; font-size:18px; color:#ef4444;">›</span>
      </div>

    </div> <!-- /sidebar-column -->
  </div> <!-- /page-container-grid -->
</div> <!-- /appMainWrapper -->

<!-- Fixed Bottom Mobile Nav -->
<div id="mobileBottomNav">
  <button type="button" class="mobile-nav-btn active" id="mbNavHome" onclick="switchMainTab('calendarPanel', this)">
    <span class="mobile-nav-btn-icon">🏠</span>
    <span>Home</span>
  </button>
  <button type="button" class="mobile-nav-btn" id="mbNavRoutine" onclick="switchMainTab('todayPanel', this)">
    <span class="mobile-nav-btn-icon">✅</span>
    <span>Routine</span>
  </button>
  <button type="button" class="mobile-nav-btn" id="mbNavGoals" onclick="switchMainTab('intentionsPanel', this)">
    <span class="mobile-nav-btn-icon">🏆</span>
    <span>Goals</span>
  </button>
  <button type="button" class="mobile-nav-btn" id="mbNavRewards" onclick="switchMainTab('rewardsVaultPanel', this)">
    <span class="mobile-nav-btn-icon">🎁</span>
    <span>Rewards</span>
  </button>
</div>
"""
        # Insert before modal html
        content = content.replace('<div id="dayModal"', mobile_bottom_html + '\n<div id="dayModal"')

    # 4. Add switchMainTab JS helper
    if 'function switchMainTab' not in content:
        tab_js = """
function switchMainTab(panelId, btnElem) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  const target = document.getElementById(panelId);
  if (target) target.classList.add('active');

  document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.sidebar-nav-item').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.mobile-nav-btn').forEach(b => b.classList.remove('active'));

  if (btnElem) btnElem.classList.add('active');

  const matchTabBtn = document.querySelector(`.tab[data-tab="${panelId}"]`);
  if (matchTabBtn) matchTabBtn.classList.add('active');
}
"""
        content = content.replace('function openModal(id) {', tab_js + '\nfunction openModal(id) {')

    with open(filepath, 'w') as f:
        f.write(content)
    print("Successfully applied template layout to:", filepath)

update_file('/Users/katrinapayne/antigravity/Growth tracker/Teen_Growth_Tracker.html')
update_file('/Users/katrinapayne/antigravity/Growth tracker/Customizable_Growth_Tracker.html')
