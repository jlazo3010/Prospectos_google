import streamlit as st
import pandas as pd
from scrap_utils import scrapear_busqueda

st.set_page_config(page_title="Scraper de Google Maps", layout="wide")

st.title("📍 Scraper de negocios en Google Maps")
st.markdown("Ingresa una búsqueda como: **'tienditas en Iztapalapa'**, **'dentistas en Guadalajara'**, etc.")

api_key = st.text_input("🔑 Ingresa tu API Key de Google Maps", type="password")
busqueda = st.text_input("🔎 Escribe tu búsqueda")

if st.button("Buscar y extraer"):
    if not busqueda or not api_key:
        st.warning("Por favor, ingresa tanto una búsqueda como tu API Key.")
    else:
        with st.spinner("Obteniendo resultados... esto puede tardar unos minutos."):
            try:
                df = scrapear_busqueda(busqueda, api_key=api_key)
                st.success(f"Se extrajeron {len(df)} resultados.")
                st.dataframe(df)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Descargar resultados en CSV",
                    data=csv,
                    file_name=f"{busqueda.replace(' ', '_')}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"❌ Error: {e}")