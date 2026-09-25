"""
PromptForge AI - Modern Dark Glassmorphic Design System & Styles.
"""

GLASS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

body {
    font-family: 'Outfit', sans-serif;
    background: radial-gradient(circle at 15% 15%, #131722 0%, #0a0c10 100%);
    color: #e2e8f0;
    min-height: 100vh;
}

code, pre, .font-mono {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Custom Scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.6);
}
::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.4);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(99, 102, 241, 0.7);
}

.glass-panel {
    background: rgba(22, 27, 34, 0.75);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    transition: all 0.25s ease-in-out;
}

.glass-panel:hover {
    border-color: rgba(99, 102, 241, 0.35);
    box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15);
}

.glass-card {
    background: rgba(30, 38, 50, 0.65);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
    transition: all 0.2s ease-in-out;
}

.glass-card:hover {
    border-color: rgba(99, 102, 241, 0.25);
}

.glow-btn {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    color: white !important;
    font-weight: 600;
    border-radius: 10px;
    box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39);
    transition: all 0.2s ease-in-out;
}

.glow-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.55);
}

.glow-btn-emerald {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white !important;
    font-weight: 600;
    border-radius: 10px;
    box-shadow: 0 4px 14px 0 rgba(16, 185, 129, 0.39);
    transition: all 0.2s ease-in-out;
}

.glow-btn-purple {
    background: linear-gradient(135deg, #a855f7 0%, #7e22ce 100%);
    color: white !important;
    font-weight: 600;
    border-radius: 10px;
    box-shadow: 0 4px 14px 0 rgba(168, 85, 247, 0.39);
    transition: all 0.2s ease-in-out;
}

.badge-tag {
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 9999px;
    background: rgba(99, 102, 241, 0.15);
    color: #818cf8;
    border: 1px solid rgba(99, 102, 241, 0.3);
}

.badge-score {
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 8px;
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #10b981;
    box-shadow: 0 0 10px #10b981;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* Tab Overrides */
.q-tab {
    text-transform: none !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em;
    padding: 8px 16px !important;
    border-radius: 10px !important;
    transition: all 0.2s ease;
}

.q-tab--active {
    background: rgba(99, 102, 241, 0.18) !important;
    color: #a5b4fc !important;
    border: 1px solid rgba(99, 102, 241, 0.35) !important;
}

.q-tab__indicator {
    display: none !important;
}

.q-tab-panels {
    background: transparent !important;
}

.q-tab-panel {
    padding: 0 !important;
}
</style>
"""
