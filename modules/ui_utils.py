import streamlit as st

def render_mini_map(address):
    """Renders a consistent small Google Map preview."""
    if address and str(address).lower() != 'nan' and address.strip() != "":
        addr_enc = address.replace(' ', '%20')
        map_url = f"https://maps.google.com/maps?q={addr_enc}&t=m&z=14&output=embed"
        st.markdown(f"""
            <div style="border-radius: 10px; overflow: hidden; margin-bottom: 10px; border: 1px solid #ddd;">
                <iframe width="100%" height="150" src="{map_url}" frameborder="0" style="border:0;"></iframe>
            </div>
        """, unsafe_allow_html=True)
        