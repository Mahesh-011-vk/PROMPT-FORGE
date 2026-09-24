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

.glass-panel {
    background: rgba(22, 27, 34, 0.7);
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
    background: rgba(30, 38, 50, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
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

.nav-link {
    color: #94a3b8 !important;
    font-weight: 500;
    transition: color 0.15s ease;
    text-decoration: none;
}

.nav-link:hover, .nav-link-active {
    color: #818cf8 !important;
}
</style>
"""
