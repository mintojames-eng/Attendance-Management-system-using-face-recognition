import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
            /* Main Background and text */
            .stApp {
                background: radial-gradient(circle at 15% 50%, #151a24 0%, #0E1117 40%, #050608 100%);
                color: #e5eaf5;
                font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
            }
            
            /* Sleek dividers */
            hr {
                border: 0;
                height: 1px;
                background-image: linear-gradient(to right, rgba(0, 224, 150, 0), rgba(0, 224, 150, 0.4), rgba(0, 224, 150, 0));
                margin-top: 2rem;
                margin-bottom: 2rem;
            }
            
            /* Hide Streamlit Branding securely while saving chevron toggle */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            header {background: transparent;}
            
            /* Buttons Styling */
            .stButton > button {
                width: 100%;
                border-radius: 12px;
                height: 3.2em;
                font-weight: 700;
                letter-spacing: 0.5px;
                transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
                border: 1px solid rgba(255,255,255,0.08);
                background: linear-gradient(180deg, #1f2533 0%, #161a24 100%);
                box-shadow: 0 4px 6px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.1);
            }
            .stButton > button:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 15px rgba(0, 224, 150, 0.25), inset 0 1px 0 rgba(255,255,255,0.15) !important;
                border-color: rgba(0, 224, 150, 0.5);
                color: #00E096;
            }
            .stButton > button:active {
                transform: translateY(1px);
                box-shadow: 0 2px 5px rgba(0, 224, 150, 0.2) !important;
            }
            
            /* Primary Button (e.g. Create Session) overrides Streamlit native matching */
            .stButton > button[kind="primary"] {
                background: linear-gradient(135deg, #00E096 0%, #00a36c 100%);
                border: none;
                color: #ffffff;
                box-shadow: 0 4px 10px rgba(0, 224, 150, 0.3);
            }
            .stButton > button[kind="primary"]:hover {
                color: #ffffff;
                box-shadow: 0 8px 20px rgba(0, 224, 150, 0.5) !important;
            }
            
            /* Inputs Styling (Text, Selectboxes) */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > div {
                border-radius: 10px !important;
                border: 1px solid rgba(255,255,255,0.08) !important;
                background-color: rgba(20, 25, 35, 0.5) !important;
                color: #ffffff !important;
                padding: 12px 15px !important;
                transition: all 0.3s ease;
            }
            
            .stTextInput > div > div > input:focus,
            .stSelectbox > div > div > div:focus {
                border-color: #00E096 !important;
                background-color: rgba(20, 25, 35, 0.8) !important;
                box-shadow: 0 0 0 2px rgba(0, 224, 150, 0.3) !important;
            }

            /* Container Cards via Glassmorphism */
            div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
                background: rgba(22, 26, 36, 0.3);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border-radius: 16px;
                padding: 24px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
                margin-bottom: 20px;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"]:hover {
                box-shadow: 0 12px 40px -10px rgba(0,224,150,0.1);
            }

            /* Tabs styling */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
                background-color: rgba(15, 20, 28, 0.4);
                border-radius: 12px;
                padding: 5px;
                margin-bottom: 10px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 45px;
                white-space: pre-wrap;
                background-color: transparent;
                border-radius: 8px;
                padding: 10px 20px;
                transition: all 0.2s ease;
                color: #8b949e;
            }
            .stTabs [aria-selected="true"] {
                background-color: #1e2430 !important;
                color: #00E096 !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                border: 1px solid rgba(255,255,255,0.05);
                border-bottom: none !important;
            }
            
            /* Metrics styling */
            [data-testid="stMetricValue"] {
                font-size: 3.5rem !important;
                color: #00B4DB;
                font-weight: 800;
                letter-spacing: -1px;
                text-shadow: 0 2px 10px rgba(0, 180, 219, 0.2);
            }
            [data-testid="stMetricLabel"] {
                font-size: 1.1rem !important;
                color: #8b949e;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1.5px;
            }
            
            /* Headings */
            h1, h2, h3 {
                font-family: 'Inter', system-ui, sans-serif !important;
                color: #E2E8F0 !important;
                font-weight: 800;
            }
            h1 {
                background: linear-gradient(120deg, #00E096, #00B4DB, #00E096);
                background-size: 200% auto;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: shine 4s linear infinite;
                letter-spacing: -0.5px;
            }
            @keyframes shine {
                to {
                    background-position: 200% center;
                }
            }
            
            /* Checkbox */
            .stCheckbox > label {
                padding-top: 5px;
                font-weight: 500;
            }
        </style>
    """, unsafe_allow_html=True)
