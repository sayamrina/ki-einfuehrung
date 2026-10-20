"""Gemeinsame Gestaltung: Farben, Karten, Badges."""
import html

import streamlit as st

CSS = """
<style>
#MainMenu, footer, [data-testid="stDecoration"] { visibility: hidden; }
.block-container, [data-testid="stMainBlockContainer"] { padding-top: 3.6rem !important; max-width: 1150px; }
.kie-hero { background: #12355b; color: #fff; padding: 18px 22px 16px; border-radius: 12px; margin-bottom: 14px; }
.kie-hero h1 { color: #fff; font-size: 25px; margin: 0; padding: 0; }
.kie-hero p { margin: 4px 0 0; opacity: .88; font-size: 14px; }
.kie-hero a { color: #bfe3f2; }
.kie-card { background: #fff; border: 1px solid #d9e2ea; border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; }
.kie-card h4 { margin: 0 0 4px; font-size: 14.5px; line-height: 1.3; color: #12355b; hyphens: auto; hyphenate-limit-chars: 14 6 5; }
.kie-muted { color: #5a6976; font-size: 13px; }
.badge { display: inline-block; white-space: nowrap; padding: 1px 9px; border-radius: 99px; font-size: 12px; font-weight: 700; margin: 0 4px 4px 0; background: #e8eef3; color: #44535f; }
.badge.ok { background: #e3f3e6; color: #1d6b3a; } .badge.warn { background: #fff3dc; color: #8a5300; }
.badge.bad { background: #fbe4e4; color: #a02a2a; }
.kie-ampel { font-size: 12px; font-weight: 700; color: #44535f; margin-top: 2px; }
.kie-ampel.ok { color: #1d6b3a; } .kie-ampel.warn { color: #8a5300; } .kie-ampel.bad { color: #a02a2a; }
.kie-col h5 { font-size: 13px; text-transform: uppercase; letter-spacing: .05em; color: #5a6976; margin: 0 0 6px; }
</style>
"""

AMPEL_BADGE = {
    "de": {"gruen": ("🟢 Datenschutz: grün", "ok"), "gelb": ("🟡 Datenschutz: gelb", "warn"),
           "rot": ("🔴 Datenschutz: rot", "bad"), "offen": ("⚪ Datenschutz: offen", "")},
    "en": {"gruen": ("🟢 Data protection: green", "ok"), "gelb": ("🟡 Data protection: amber", "warn"),
           "rot": ("🔴 Data protection: red", "bad"), "offen": ("⚪ Data protection: open", "")},
}


def ampel_badge(level: str) -> tuple[str, str]:
    from .i18n import lang

    return AMPEL_BADGE[lang()][level]


def esc(text) -> str:
    return html.escape(str(text))


def badge(text: str, kind: str = "") -> str:
    return f'<span class="badge {kind}">{esc(text)}</span>'


def hero(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="kie-hero"><h1>{esc(title)}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)
