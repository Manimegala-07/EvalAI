const style = document.createElement("style");
style.textContent = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --cream: #FAF8F4;
    --white: #FFFFFF;
    --ink: #1A1A2E;
    --ink-light: #4A4A6A;
    --ink-muted: #8888AA;
    --accent: #2D5BE3;
    --accent-light: #EEF2FF;
    --accent-soft: #C7D4FA;
    --green: #16A34A;
    --green-light: #DCFCE7;
    --red: #DC2626;
    --red-light: #FEE2E2;
    --amber: #D97706;
    --amber-light: #FEF3C7;
    --border: #E8E6F0;
    --shadow-sm: 0 1px 3px rgba(26,26,46,0.08);
    --shadow-md: 0 4px 16px rgba(26,26,46,0.10);
    --shadow-lg: 0 8px 32px rgba(26,26,46,0.13);
    --radius: 12px;
    --radius-sm: 8px;
    --radius-lg: 20px;
  }

  html, body { height: 100%; }
  #root { height: 100%; font-family: 'DM Sans', sans-serif; background: var(--cream); color: var(--ink); font-size: 15px; line-height: 1.6; }
  h1, h2, h3, h4 { font-family: 'DM Serif Display', serif; letter-spacing: -0.02em; }

  .app-shell { display: flex; min-height: 100vh; width: 100%; overflow: hidden; }
  .sidebar { width: 260px; min-height: 100vh; background: var(--white); border-right: 1px solid var(--border); display: flex; flex-direction: column; position: fixed; top: 0; left: 0; z-index: 100; box-shadow: var(--shadow-sm); }
  .sidebar-logo { padding: 28px 24px 20px; border-bottom: 1px solid var(--border); }
  .sidebar-logo h2 { font-size: 20px; color: var(--accent); }
  .sidebar-logo p { font-size: 12px; color: var(--ink-muted); font-weight: 300; margin-top: 2px; }
  .sidebar-nav { flex: 1; padding: 16px 12px; }
  .nav-section-label { font-size: 10px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-muted); padding: 8px 12px 4px; }
  .nav-item { display: flex; align-items: center; gap: 10px; padding: 11px 14px; border-radius: var(--radius-sm); cursor: pointer; font-size: 14px; font-weight: 400; color: var(--ink-light); margin-bottom: 2px; transition: all 0.15s ease; border: none; background: none; width: 100%; text-align: left; }
  .nav-item:hover { background: var(--accent-light); color: var(--accent); }
  .nav-item.active { background: var(--accent-light); color: var(--accent); font-weight: 600; }
  .nav-item .nav-icon { font-size: 16px; width: 20px; text-align: center; }
  .sidebar-footer { padding: 16px; border-top: 1px solid var(--border); }
  .user-chip { display: flex; align-items: center; gap: 12px; padding: 12px 14px; background: var(--cream); border-radius: var(--radius-sm); }
  .user-avatar { width: 36px; height: 36px; border-radius: 50%; background: var(--accent); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 14px; flex-shrink: 0; overflow: hidden; }
  .user-info { flex: 1; min-width: 0; }
  .user-info .name { font-size: 14px; font-weight: 600; color: var(--ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .user-info .role { font-size: 12px; color: var(--ink-muted); text-transform: capitalize; }
  .logout-btn { background: none; border: none; cursor: pointer; color: var(--ink-muted); font-size: 18px; padding: 4px; border-radius: 4px; transition: color 0.15s; }
  .logout-btn:hover { color: var(--red); }

  .main-content { margin-left: 260px; flex: 1; min-height: 100vh; background: var(--cream); min-width: 0; overflow-x: hidden; }
  .page-inner { max-width: 1100px; width: 100%; margin: 0 auto; }
  .page-header { padding: 28px 36px 16px; display: flex; flex-direction: column; gap: 4px; }
  .page-header h1 { font-size: 26px; color: var(--ink); margin: 0; }
  .page-header p { color: var(--ink-muted); margin: 2px 0 0; font-size: 13.5px; }

  .page-body { padding: 16px 36px 48px; max-width: 100%; }
  .card { background: var(--white); border-radius: var(--radius); border: 1px solid var(--border); box-shadow: var(--shadow-sm); }
  .card-pad { padding: 28px 32px; }

  .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; }
  .stat-card { background: var(--white); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px 24px; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; justify-content: center; }
  .stat-card .stat-label { font-size: 11px; color: var(--ink-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; }
  .stat-card .stat-value { font-size: 30px; font-family: 'DM Serif Display', serif; color: var(--ink); margin: 6px 0 4px; line-height: 1; }
  .stat-card .stat-sub { font-size: 12px; color: var(--ink-muted); }
  .stat-card.accent { background: var(--accent); border-color: var(--accent); }
  .stat-card.accent .stat-label, .stat-card.accent .stat-value, .stat-card.accent .stat-sub { color: white; }

  .btn {
    display: inline-flex; align-items: center; justify-content: center;
    gap: 8px; padding: 10px 20px; border-radius: var(--radius-sm);
    font-size: 14px; font-weight: 500; cursor: pointer; border: none;
    transition: all 0.15s ease; font-family: 'DM Sans', sans-serif;
    min-width: 120px; text-align: center; white-space: nowrap;
  }
  .btn-primary { background: var(--accent); color: white; }
  .btn-primary:hover { background: #2449C0; box-shadow: var(--shadow-md); }
  .btn-secondary { background: var(--white); color: var(--ink); border: 1px solid var(--border); }
  .btn-secondary:hover { background: var(--cream); border-color: var(--accent-soft); }
  .btn-danger { background: var(--red); color: white; }
  .btn-success { background: var(--green); color: white; }
  .btn-lg { padding: 12px 32px; font-size: 15px; min-width: 160px; }
  .btn-sm { padding: 7px 14px; font-size: 13px; min-width: 90px; }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; }

  .form-group { margin-bottom: 20px; }
  .form-label { display: block; font-size: 13.5px; font-weight: 500; color: var(--ink); margin-bottom: 8px; }
  .form-input, .form-select, .form-textarea {
    width: 100%; padding: 11px 16px; border: 1px solid var(--border);
    border-radius: var(--radius-sm); font-size: 14px; font-family: 'DM Sans', sans-serif;
    color: var(--ink); background: var(--white); transition: border-color 0.18s, box-shadow 0.18s;
    line-height: 1.5;
  }
  .form-input:focus, .form-select:focus, .form-textarea:focus {
    border-color: var(--accent); box-shadow: 0 0 0 4px var(--accent-light); outline: none;
  }
  .form-textarea { min-height: 120px; resize: vertical; }

  .table-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; }
  thead tr { border-bottom: 2px solid var(--border); background: #f8f9fc; }
  tbody tr { border-bottom: 1px solid var(--border); transition: background 0.14s; }
  tbody tr:hover { background: var(--accent-light); }
  th { font-size: 12px; font-weight: 600; color: var(--ink-muted); text-transform: uppercase; letter-spacing: 0.05em; padding: 14px 20px; text-align: left; }
  td { padding: 14px 20px; font-size: 14px; color: var(--ink); }

  .badge { display: inline-flex; align-items: center; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; }
  .badge-green { background: var(--green-light); color: var(--green); }
  .badge-red { background: var(--red-light); color: var(--red); }
  .badge-amber { background: var(--amber-light); color: var(--amber); }
  .badge-blue { background: var(--accent-light); color: var(--accent); }
  .badge-gray { background: #F3F4F6; color: #6B7280; }

  .auth-shell { min-height: 100vh; display: flex; background: var(--cream); }
  .auth-left { width: 360px; flex-shrink: 0; background: var(--accent); display: flex; flex-direction: column; justify-content: center; padding: 48px 40px; color: white; }
  .auth-left h1 { font-size: 34px; color: white; line-height: 1.15; }
  .auth-left p { font-size: 14px; opacity: 0.8; margin-top: 12px; line-height: 1.7; }
  .auth-feature { display: flex; align-items: flex-start; gap: 12px; margin-top: 24px; }
  .auth-feature-icon { font-size: 18px; margin-top: 2px; }
  .auth-feature-text { font-size: 13.5px; opacity: 0.85; }
  .auth-right { flex: 1; display: flex; align-items: center; justify-content: center; padding: 32px 24px; }
  .auth-card { width: 100%; max-width: 400px; background: var(--white); border-radius: var(--radius-lg); padding: 36px; box-shadow: var(--shadow-lg); border: 1px solid var(--border); }
  .auth-card h2 { font-size: 22px; margin-bottom: 4px; }
  .auth-card .subtitle { color: var(--ink-muted); font-size: 13.5px; margin-bottom: 24px; }
  .auth-switch { text-align: center; margin-top: 18px; font-size: 13.5px; color: var(--ink-muted); }
  .auth-switch button { background: none; border: none; color: var(--accent); cursor: pointer; font-weight: 600; font-size: 13.5px; }

  .role-toggle { display: flex; gap: 8px; margin-bottom: 24px; }
  .role-btn { flex: 1; padding: 12px; border-radius: var(--radius-sm); border: 2px solid var(--border); background: var(--white); cursor: pointer; font-size: 14px; font-weight: 500; color: var(--ink-light); transition: all 0.15s; text-align: center; }
  .role-btn.active { border-color: var(--accent); background: var(--accent-light); color: var(--accent); }

  .profile-banner { background: linear-gradient(135deg, var(--accent) 0%, #1A3A9E 100%); border-radius: var(--radius) var(--radius) 0 0; padding: 40px 40px 72px; color: white; position: relative; }
  .profile-institution { font-size: 12px; opacity: 0.7; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px; }
  .profile-name { font-size: 32px; color: white; }
  .profile-email { opacity: 0.8; font-size: 14px; margin-top: 6px; }
  .profile-avatar-lg { width: 90px; height: 90px; border-radius: 50%; background: rgba(255,255,255,0.25); border: 3px solid rgba(255,255,255,0.5); display: flex; align-items: center; justify-content: center; font-size: 32px; font-weight: 700; color: white; margin-bottom: 20px; overflow: hidden; }
  .profile-body { margin-top: -48px; padding: 0 40px 40px; }

  .heatmap-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
  .heatmap-label { font-size: 13px; font-weight: 500; width: 120px; color: var(--ink); }
  .heatmap-bar-track { flex: 1; height: 10px; background: var(--border); border-radius: 99px; overflow: hidden; }
  .heatmap-bar-fill { height: 100%; border-radius: 99px; transition: width 0.6s ease; }
  .heatmap-pct { font-size: 12px; color: var(--ink-muted); width: 40px; text-align: right; }

  .tabs { display: flex; gap: 4px; border-bottom: 2px solid var(--border); margin-bottom: 24px; }
  .tab-btn { padding: 10px 20px; font-size: 14px; font-weight: 500; background: none; border: none; cursor: pointer; color: var(--ink-muted); border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all 0.15s; }
  .tab-btn.active { color: var(--accent); border-bottom-color: var(--accent); }

  .modal-overlay { position: fixed; inset: 0; background: rgba(26,26,46,0.4); display: flex; align-items: center; justify-content: center; z-index: 999; padding: 20px; }
  .modal { background: var(--white); border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); width: 100%; max-width: 620px; max-height: 90vh; overflow-y: auto; }
  .modal-header { padding: 24px 32px 16px; display: flex; align-items: center; justify-content: space-between; }
  .modal-header h3 { font-size: 20px; margin: 0; }
  .modal-close { background: none; border: none; cursor: pointer; font-size: 24px; color: var(--ink-muted); padding: 4px; }
  .modal-body { padding: 0 32px 32px; }

  .alert { padding: 12px 16px; border-radius: var(--radius-sm); font-size: 14px; margin-bottom: 16px; }
  .alert-error { background: var(--red-light); color: var(--red); }
  .alert-success { background: var(--green-light); color: var(--green); }
  .alert-info { background: var(--accent-light); color: var(--accent); }

  .search-bar { position: relative; display: flex; align-items: center; flex: 1; max-width: 360px; }
  .search-bar input { padding-left: 40px !important; }
  .search-icon { position: absolute; left: 14px; font-size: 15px; color: var(--ink-muted); pointer-events: none; }

  .q-card { background: var(--white); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px 24px; margin-bottom: 12px; transition: box-shadow 0.15s, border-color 0.15s; }
  .q-card:hover { box-shadow: var(--shadow-md); border-color: var(--accent-soft); }
  .q-card.selected { border-color: var(--accent); background: var(--accent-light); }
  .q-text { font-size: 14.5px; color: var(--ink); margin-bottom: 8px; font-weight: 500; }
  .q-answer { font-size: 13px; color: var(--ink-muted); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

  .answer-block { background: var(--white); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px; margin-bottom: 20px; }
  .answer-block .q-num { font-size: 11.5px; color: var(--ink-muted); text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; margin-bottom: 8px; }
  .answer-block .q-text { font-size: 15.5px; font-weight: 600; margin-bottom: 14px; }

  @keyframes spin { to { transform: rotate(360deg); } }
  .spinner { width: 20px; height: 20px; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.6s linear infinite; }

  .feedback-card { background: linear-gradient(135deg, #EEF2FF 0%, #F8F0FF 100%); border: 1px solid var(--accent-soft); border-radius: var(--radius); padding: 20px 24px; }
  .feedback-card h4 { font-size: 14px; color: var(--accent); margin-bottom: 10px; }
  .feedback-card p { font-size: 14px; color: var(--ink); line-height: 1.7; }

  .empty-state { text-align: center; padding: 64px 24px; color: var(--ink-muted); }
  .empty-state .icon { font-size: 48px; margin-bottom: 16px; }
  .empty-state p { font-size: 15px; }

  .validation-panel { background: var(--cream); border-radius: var(--radius-sm); padding: 16px 20px; margin-top: 16px; border-left: 4px solid var(--accent); }

  .flex { display: flex; }
  .flex-col { flex-direction: column; }
  .items-center { align-items: center; }
  .items-start { align-items: flex-start; }
  .justify-between { justify-content: space-between; }
  .justify-end { justify-content: flex-end; }
  .gap-2 { gap: 8px; }
  .gap-3 { gap: 12px; }
  .gap-4 { gap: 16px; }
  .gap-6 { gap: 24px; }
  .mt-1 { margin-top: 4px; }
  .mt-2 { margin-top: 8px; }
  .mt-3 { margin-top: 12px; }
  .mt-4 { margin-top: 16px; }
  .mt-6 { margin-top: 24px; }
  .mb-2 { margin-bottom: 8px; }
  .mb-4 { margin-bottom: 16px; }
  .mb-6 { margin-bottom: 24px; }
  .w-full { width: 100%; }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
  .text-sm { font-size: 13px; }
  .text-xs { font-size: 12px; }
  .text-muted { color: var(--ink-muted); }
  .font-600 { font-weight: 600; }
  .section-title { font-size: 18px; margin-bottom: 16px; }
  .divider { height: 1px; background: var(--border); margin: 24px 0; }
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: var(--cream); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
`;
document.head.appendChild(style);
