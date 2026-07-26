import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
            /* Main Background and text */
            .stApp {
                background-color: #0E1117;
                color: #FAFAFA;
            }
            
            /* Hide Streamlit Branding */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            header {background: transparent;}
            
            /* Buttons Styling */
            .stButton > button {
                width: 100%;
                border-radius: 8px;
                height: 3em;
                font-weight: 600;
                transition: all 0.3s ease;
                border: 1px solid #1f2733;
                background-color: #1E222A;
            }
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,224,150,0.2) !important;
                border-color: #00E096;
                color: #00E096;
            }
            .stButton > button[data-baseweb="button"] {
                /* Primary button specifically */
            }
            
            /* Inputs Styling (Text, Selectboxes) */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > div {
                border-radius: 8px !important;
                border: 1px solid #2b3543 !important;
                background-color: #151920 !important;
                color: white !important;
                padding: 10px !important;
            }
            
            .stTextInput > div > div > input:focus,
            .stSelectbox > div > div > div:focus {
                border-color: #00E096 !important;
                box-shadow: 0 0 0 1px #00E096 !important;
            }

            /* Container Cards */
            div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
                background: linear-gradient(145deg, #161922, #1a1e27);
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #232a35;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 15px;
            }

            /* Tabs styling */
            .stTabs [data-baseweb="tab-list"] {
                gap: 24px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: transparent;
                border-radius: 4px 4px 0px 0px;
                gap: 1px;
                padding-top: 10px;
                padding-bottom: 10px;
            }
            .stTabs [aria-selected="true"] {
                border-bottom: 2px solid #00E096 !important;
                color: #00E096 !important;
                font-weight: 600;
            }
            
            /* Metrics styling */
            [data-testid="stMetricValue"] {
                font-size: 3rem !important;
                color: #00E096;
                font-weight: 700;
            }
            [data-testid="stMetricLabel"] {
                font-size: 1rem !important;
                color: #a3a8b8;
                font-weight: 500;
            }
            
            /* Headings */
            h1, h2, h3 {
                font-family: 'Inter', sans-serif !important;
                color: #E2E8F0 !important;
                font-weight: 800;
            }
            h1 {
                background: -webkit-linear-gradient(45deg, #00E096, #00B4DB);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            /* Checkbox */
            .stCheckbox > label {
                padding-top: 5px;
                font-weight: 500;
            }
        </style>
    """, unsafe_allow_html=True)
