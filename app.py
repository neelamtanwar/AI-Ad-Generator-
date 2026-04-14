# app.py — Bold & Colorful Step-by-Step Wizard UI
# Replace your existing app.py with this entire file

import io
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Must be the very first Streamlit call ─────────────────────────────────
st.set_page_config(
    page_title="AI Ad Creative Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Global CSS — bold gradients, custom fonts, card styles ────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 860px !important;
}

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #6C3FE8 0%, #E8399A 50%, #FF6B35 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(108,63,232,0.35);
}
.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: white !important;
    margin: 0 0 0.4rem 0;
    letter-spacing: -0.5px;
}
.hero p {
    color: rgba(255,255,255,0.88);
    font-size: 1.05rem;
    margin: 0;
}

/* ── Step indicator ── */
.steps-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    margin-bottom: 2rem;
}
.step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
}
.step-circle {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    transition: all 0.3s;
}
.step-circle.done {
    background: linear-gradient(135deg, #6C3FE8, #E8399A);
    color: white;
    box-shadow: 0 4px 12px rgba(108,63,232,0.4);
}
.step-circle.active {
    background: linear-gradient(135deg, #FF6B35, #E8399A);
    color: white;
    box-shadow: 0 4px 16px rgba(232,57,154,0.5);
    transform: scale(1.15);
}
.step-circle.inactive {
    background: #f0f0f0;
    color: #aaa;
}
.step-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #888;
}
.step-label.active { color: #E8399A; }
.step-label.done   { color: #6C3FE8; }
.step-connector {
    width: 60px;
    height: 2px;
    margin-bottom: 22px;
    background: linear-gradient(90deg, #6C3FE8, #E8399A);
    opacity: 0.25;
}
.step-connector.done { opacity: 1; }

/* ── Section card ── */
.section-card {
    background: white;
    border-radius: 16px;
    padding: 1.8rem;
    margin-bottom: 1.2rem;
    border: 1.5px solid #f0eeff;
    box-shadow: 0 2px 16px rgba(108,63,232,0.07);
}
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.pill {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
}
.pill-purple { background: #ede8fd; color: #6C3FE8; }
.pill-pink   { background: #fde8f5; color: #E8399A; }
.pill-orange { background: #fff0eb; color: #FF6B35; }

/* ── Streamlit widget overrides ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    border-radius: 10px !important;
    border: 1.5px solid #e8e0ff !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6C3FE8 !important;
    box-shadow: 0 0 0 3px rgba(108,63,232,0.12) !important;
}

/* ── Generate button ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #6C3FE8 0%, #E8399A 60%, #FF6B35 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
    box-shadow: 0 6px 20px rgba(108,63,232,0.35) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 28px rgba(108,63,232,0.45) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Result cards ── */
.result-hero {
    background: linear-gradient(135deg, #6C3FE8, #E8399A);
    border-radius: 16px;
    padding: 1.6rem;
    margin-bottom: 1rem;
    color: white;
}
.result-hero .label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    opacity: 0.8;
    margin-bottom: 6px;
}
.result-hero .value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.55rem;
    font-weight: 700;
    line-height: 1.3;
}
.result-card {
    background: white;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
    border: 1.5px solid #f0eeff;
    box-shadow: 0 2px 10px rgba(108,63,232,0.06);
}
.result-card .label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #6C3FE8;
    margin-bottom: 6px;
}
.result-card .value {
    font-size: 0.97rem;
    color: #222;
    line-height: 1.55;
}
.cta-badge {
    display: inline-block;
    background: linear-gradient(135deg, #FF6B35, #E8399A);
    color: white;
    padding: 8px 22px;
    border-radius: 25px;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    margin-top: 4px;
    box-shadow: 0 4px 14px rgba(255,107,53,0.4);
}

/* ── Social preview mock ── */
.social-mock {
    background: #fafafa;
    border-radius: 14px;
    border: 1.5px solid #ececec;
    overflow: hidden;
    font-family: 'Inter', sans-serif;
}
.social-mock-header {
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    border-bottom: 1px solid #ececec;
    background: white;
}
.avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg,#6C3FE8,#E8399A);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    font-size: 0.85rem;
}
.social-mock-body {
    padding: 14px;
}
.social-mock-img {
    width: 100%;
    height: 160px;
    background: linear-gradient(135deg,#ede8fd,#fde8f5);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6C3FE8;
    font-weight: 600;
    font-size: 0.85rem;
    margin-bottom: 10px;
}

/* ── Nav buttons ── */
.nav-row {
    display: flex;
    gap: 12px;
    margin-top: 1.2rem;
}

/* ── Divider ── */
.grad-divider {
    height: 3px;
    background: linear-gradient(90deg, #6C3FE8, #E8399A, #FF6B35);
    border-radius: 2px;
    margin: 1.5rem 0;
    opacity: 0.5;
}
</style>
""", unsafe_allow_html=True)

# ── Import agent modules ──────────────────────────────────────────────────
try:
    from agent.llm_core import generate_ad_copy, PLATFORM_SPECS
    from agent.image_gen import generate_flyer
    from agent.video_gen import create_video_ad
    MODULES_LOADED = True
except ImportError as e:
    MODULES_LOADED = False
    IMPORT_ERROR = str(e)
    # Provide helpful error guidance
    if "llm_core" in IMPORT_ERROR:
        IMPORT_ERROR += "\n\n💡 Try: `pip install groq python-dotenv`"
    elif "image_gen" in IMPORT_ERROR:
        IMPORT_ERROR += "\n\n💡 Try: `pip install requests pillow`"
    elif "video_gen" in IMPORT_ERROR:
        IMPORT_ERROR += "\n\n💡 Try: `pip install gTTS moviepy`"
    else:
        IMPORT_ERROR += "\n\n💡 Try: `pip install -r requirements.txt`"

# ── Session state initialisation ─────────────────────────────────────────
defaults = {
    "step": 1,
    "brief": {},
    "ad_copy": None,
    "flyer_img": None,
    "video_path": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helper: step indicator HTML ──────────────────────────────────────────
STEP_LABELS = ["Product", "Audience", "Ad Specs", "Generate"]

def render_steps(current: int):
    html = '<div class="steps-row">'
    for i, label in enumerate(STEP_LABELS, start=1):
        if i < current:
            cls_c, cls_l = "done", "done"
            icon = "✓"
        elif i == current:
            cls_c, cls_l = "active", "active"
            icon = str(i)
        else:
            cls_c, cls_l = "inactive", ""
            icon = str(i)
        html += f'''
        <div class="step-item">
            <div class="step-circle {cls_c}">{icon}</div>
            <div class="step-label {cls_l}">{label}</div>
        </div>'''
        if i < len(STEP_LABELS):
            connector_cls = "done" if i < current else ""
            html += f'<div class="step-connector {connector_cls}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🎯 AI Ad Creative Agent</h1>
    <p>Answer 3 quick steps — get a complete, platform-ready ad powered by Llama 3.3</p>
</div>
""", unsafe_allow_html=True)

if not MODULES_LOADED:
    st.error(f"⚠️ Could not load agent modules: {IMPORT_ERROR}")
    st.info("Make sure you've run `pip install -r requirements.txt` with your venv active.")
    st.stop()

# ═══════════════════════════════════════════════════════
# STEP 1 — Product & Company
# ═══════════════════════════════════════════════════════
if st.session_state.step == 1:
    render_steps(1)

    st.markdown("""
    <div class="section-card">
        <div class="section-title">
            📦 <span>Product & Company</span>
            <span class="pill pill-purple">Step 1 of 3</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    product_name = col1.text_input("🏷️ Product name *",
        value=st.session_state.brief.get("product_name", ""),
        placeholder="e.g. EcoBottle Pro")
    company_name = col2.text_input("🏢 Company name *",
        value=st.session_state.brief.get("company_name", ""),
        placeholder="e.g. GreenLife Co.")

    product_desc = st.text_area("✨ What makes it special? (USP) *",
        value=st.session_state.brief.get("product_description", ""),
        placeholder="e.g. Insulated water bottle that keeps drinks cold 48h, made from 100% recycled ocean plastic. Available in 12 colours.",
        height=110)

    brand_voice = st.text_input("🎨 Brand personality / voice",
        value=st.session_state.brief.get("brand_voice", ""),
        placeholder="e.g. Playful, eco-conscious, speaks to millennials")

    st.markdown('<div class="grad-divider"></div>', unsafe_allow_html=True)

    if st.button("Next → Audience Details", key="next1"):
        if not product_name.strip() or not company_name.strip() or not product_desc.strip():
            st.error("⚠️ Please fill in Product name, Company name, and the USP description.")
        else:
            st.session_state.brief.update({
                "product_name": product_name.strip(),
                "company_name": company_name.strip(),
                "product_description": product_desc.strip(),
                "brand_voice": brand_voice.strip() or "Professional and friendly",
            })
            st.session_state.step = 2
            st.rerun()

# ═══════════════════════════════════════════════════════
# STEP 2 — Audience & Goals
# ═══════════════════════════════════════════════════════
elif st.session_state.step == 2:
    render_steps(2)

    st.markdown("""
    <div class="section-card">
        <div class="section-title">
            🎯 <span>Target Audience & Goals</span>
            <span class="pill pill-pink">Step 2 of 3</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    target_audience = st.text_input("👥 Who is your target audience? *",
        value=st.session_state.brief.get("target_audience", ""),
        placeholder="e.g. Eco-conscious 25–35 year olds, fitness enthusiasts, urban professionals")

    col3, col4 = st.columns(2)
    cta_goal = col3.text_input("🚀 Campaign goal / CTA *",
        value=st.session_state.brief.get("cta_goal", ""),
        placeholder="e.g. Shop Now  |  Get 20% Off  |  Sign Up Free")

    tone = col4.selectbox("🎭 Ad tone",
        ["Professional", "Funny & Playful", "Inspirational",
         "Urgent / FOMO", "Friendly & Warm", "Luxury & Premium"],
        index=["Professional", "Funny & Playful", "Inspirational",
               "Urgent / FOMO", "Friendly & Warm", "Luxury & Premium"]
               .index(st.session_state.brief.get("tone", "Professional")))

    special_notes = st.text_area("📝 Any special instructions? (optional)",
        value=st.session_state.brief.get("special_notes", ""),
        placeholder="e.g. Mention our summer sale ends Sunday. Highlight the 2-year warranty.",
        height=90)

    st.markdown('<div class="grad-divider"></div>', unsafe_allow_html=True)

    col_back, col_next = st.columns([1, 2])
    if col_back.button("← Back", key="back2"):
        st.session_state.step = 1
        st.rerun()
    if col_next.button("Next → Ad Specifications", key="next2"):
        if not target_audience.strip() or not cta_goal.strip():
            st.error("⚠️ Please fill in the target audience and campaign goal.")
        else:
            st.session_state.brief.update({
                "target_audience": target_audience.strip(),
                "cta_goal": cta_goal.strip(),
                "tone": tone,
                "special_notes": special_notes.strip(),
            })
            st.session_state.step = 3
            st.rerun()

# ═══════════════════════════════════════════════════════
# STEP 3 — Ad Specs
# ═══════════════════════════════════════════════════════
elif st.session_state.step == 3:
    render_steps(3)

    st.markdown("""
    <div class="section-card">
        <div class="section-title">
            ⚙️ <span>Ad Format & Platform</span>
            <span class="pill pill-orange">Step 3 of 3</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Ad type cards
    st.markdown("**Choose your ad format:**")
    col_t, col_i, col_v = st.columns(3)

    current_type = st.session_state.brief.get("ad_type", "Text Ad")

    def type_card(col, icon, title, desc, key):
        selected = current_type == title
        border = "3px solid #6C3FE8" if selected else "1.5px solid #f0eeff"
        bg = "#faf8ff" if selected else "white"
        col.markdown(f"""
        <div style="background:{bg}; border:{border}; border-radius:14px;
                    padding:1.1rem; text-align:center; cursor:pointer;
                    box-shadow: {'0 4px 16px rgba(108,63,232,0.15)' if selected else 'none'}">
            <div style="font-size:2rem">{icon}</div>
            <div style="font-family:'Space Grotesk',sans-serif; font-weight:700;
                        font-size:0.95rem; margin:6px 0 4px; color:{'#6C3FE8' if selected else '#222'}">{title}</div>
            <div style="font-size:0.78rem; color:#888">{desc}</div>
        </div>""", unsafe_allow_html=True)
        return col.button("Select" if not selected else "✓ Selected",
                          key=key, use_container_width=True)

    if type_card(col_t, "📝", "Text Ad", "Copy only, fast", "sel_text"):
        st.session_state.brief["ad_type"] = "Text Ad"; st.rerun()
    if type_card(col_i, "🖼️", "Image Flyer", "Visual + copy", "sel_img"):
        st.session_state.brief["ad_type"] = "Image Flyer"; st.rerun()
    if type_card(col_v, "🎬", "Video Ad", "Video + voiceover", "sel_vid"):
        st.session_state.brief["ad_type"] = "Video Ad"; st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    available_platforms = list(PLATFORM_SPECS.keys())
    default_platform = st.session_state.brief.get("platform", "Instagram Square")
    # Safe index lookup
    try:
        default_idx = available_platforms.index(default_platform)
    except ValueError:
        default_idx = 0  # Fall back to first if not found

    platform = st.selectbox("📱 Target platform",
        available_platforms,
        index=default_idx)

    # Brief summary
    b = st.session_state.brief
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#ede8fd,#fde8f5); border-radius:14px;
                padding:1.2rem 1.4rem; margin-top:1rem;">
        <div style="font-family:'Space Grotesk',sans-serif; font-weight:700;
                    font-size:0.85rem; color:#6C3FE8; margin-bottom:10px;
                    text-transform:uppercase; letter-spacing:0.5px;">📋 Your Brief Summary</div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:0.88rem;">
            <div><b>Product:</b> {b.get('product_name','—')}</div>
            <div><b>Company:</b> {b.get('company_name','—')}</div>
            <div><b>Audience:</b> {b.get('target_audience','—')}</div>
            <div><b>Tone:</b> {b.get('tone','—')}</div>
            <div><b>CTA:</b> {b.get('cta_goal','—')}</div>
            <div><b>Format:</b> {b.get('ad_type','Text Ad')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="grad-divider"></div>', unsafe_allow_html=True)

    col_back2, col_gen = st.columns([1, 2])
    if col_back2.button("← Back", key="back3"):
        st.session_state.step = 2
        st.rerun()
    if col_gen.button("✨ Generate My Ad Now!", key="generate"):
        st.session_state.brief["platform"] = platform
        if "ad_type" not in st.session_state.brief or not st.session_state.brief["ad_type"]:
            st.session_state.brief["ad_type"] = "Image Flyer"  # Safe default
        st.session_state.step = 4
        st.rerun()

# ═══════════════════════════════════════════════════════
# STEP 4 — Generate & Show Results
# ═══════════════════════════════════════════════════════
elif st.session_state.step == 4:
    render_steps(4)

    brief = st.session_state.brief

    # Only generate if we don't already have results
    if st.session_state.ad_copy is None:
        with st.status("🤖 Agent is crafting your ad...", expanded=True) as status:
            st.write("📝 Llama 3.3 is writing your copy...")
            try:
                ad_copy = generate_ad_copy(brief)
                st.session_state.ad_copy = ad_copy
                st.write("✅ Copy ready!")
            except Exception as e:
                st.error(f"❌ Failed to generate ad copy: {e}")
                st.stop()

            if brief.get("ad_type") in ["Image Flyer", "Video Ad"]:
                st.write("🖼️ Generating image with Pollinations.ai... (20–40s)")
                try:
                    flyer = generate_flyer(ad_copy, brief["platform"])
                    st.session_state.flyer_img = flyer
                    st.write("✅ Image ready!")
                except Exception as e:
                    st.warning(f"Image issue: {e}")

            if brief.get("ad_type") == "Video Ad" and st.session_state.flyer_img:
                st.write("🎙️ Creating voiceover & assembling video...")
                try:
                    vpath = create_video_ad(
                        st.session_state.flyer_img, ad_copy["video_script"])
                    st.session_state.video_path = vpath
                    st.write("✅ Video ready!")
                except Exception as e:
                    st.warning(f"Video issue: {e}")

            status.update(label="🎉 Your ad is ready!", state="complete")

    # ── Show results ─────────────────────────────────────────────────────
    ad_copy = st.session_state.ad_copy
    if ad_copy:
        st.markdown("""
        <div style="text-align:center; margin:1rem 0 1.5rem;">
            <div style="font-family:'Space Grotesk',sans-serif; font-size:1.6rem;
                        font-weight:700; background:linear-gradient(135deg,#6C3FE8,#E8399A,#FF6B35);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                🎉 Your Ad is Ready!
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1.1, 0.9], gap="large")

        with col_left:
            # Headline card
            st.markdown(f"""
            <div class="result-hero">
                <div class="label">✏️ Headline</div>
                <div class="value">{ad_copy['headline']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Body copy card
            st.markdown(f"""
            <div class="result-card">
                <div class="label">📄 Body Copy</div>
                <div class="value">{ad_copy['body']}</div>
            </div>
            """, unsafe_allow_html=True)

            # CTA card
            st.markdown(f"""
            <div class="result-card">
                <div class="label">🚀 Call to Action</div>
                <div class="value">
                    <span class="cta-badge">{ad_copy['cta']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Rationale
            with st.expander("💡 Creative Rationale"):
                st.write(ad_copy.get("rationale", ""))
            if brief.get("ad_type") == "Video Ad":
                with st.expander("🎙️ Voiceover Script"):
                    st.write(ad_copy.get("video_script", ""))
            with st.expander("🔍 Image Prompt Used"):
                st.caption(ad_copy.get("image_prompt", ""))

        with col_right:
            # Social media mock preview
            initials = "".join([w[0].upper() for w in brief.get('company_name','AD').split()[:2]])
            st.markdown(f"""
            <div class="social-mock">
                <div class="social-mock-header">
                    <div class="avatar">{initials}</div>
                    <div>
                        <div style="font-weight:600; font-size:0.88rem;">
                            {brief.get('company_name','Your Brand')}</div>
                        <div style="font-size:0.75rem; color:#888;">
                            Sponsored · {brief.get('platform','')}</div>
                    </div>
                </div>
                <div class="social-mock-body">
                    <div class="social-mock-img">📸 Your image appears here</div>
                    <div style="font-weight:700; font-size:0.92rem; margin-bottom:5px; color:#111;">
                        {ad_copy['headline']}</div>
                    <div style="font-size:0.82rem; color:#555; margin-bottom:10px; line-height:1.45;">
                        {ad_copy['body'][:90]}{'...' if len(ad_copy['body'])>90 else ''}</div>
                    <div style="background:linear-gradient(135deg,#FF6B35,#E8399A);
                                color:white; padding:6px 16px; border-radius:20px;
                                display:inline-block; font-size:0.82rem; font-weight:700;">
                        {ad_copy['cta']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Show actual flyer image if generated
            if st.session_state.flyer_img:
                st.markdown("<br>", unsafe_allow_html=True)
                st.image(st.session_state.flyer_img, use_column_width=True,
                         caption="Generated Flyer")
                buf = io.BytesIO()
                st.session_state.flyer_img.save(buf, format="PNG")
                buf.seek(0)  # Reset buffer position before reading
                st.download_button(
                    "⬇️ Download Flyer (PNG)", buf.getvalue(),
                    file_name=f"{brief['product_name'].replace(' ','_')}_ad.png",
                    mime="image/png", use_container_width=True)

            if st.session_state.video_path and \
               os.path.exists(st.session_state.video_path):
                st.video(st.session_state.video_path)
                with open(st.session_state.video_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Video (MP4)", f.read(),
                        file_name=f"{brief['product_name'].replace(' ','_')}_ad.mp4",
                        mime="video/mp4", use_container_width=True)

        st.markdown('<div class="grad-divider"></div>', unsafe_allow_html=True)

        # Reset button
        col_r1, col_r2, col_r3 = st.columns([1, 1, 1])
        if col_r2.button("🔄 Create Another Ad", key="reset"):
            # Cleanup temp files before reset
            if st.session_state.video_path and os.path.exists(st.session_state.video_path):
                try:
                    os.unlink(st.session_state.video_path)
                except Exception:
                    pass  # Silent cleanup failure
            # Reset session state
            for k in ["step", "brief", "ad_copy", "flyer_img", "video_path"]:
                st.session_state[k] = defaults[k]
            st.rerun()