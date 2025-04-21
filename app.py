import streamlit as st
import pandas as pd
from scrap_utils import scrapear_busqueda

st.set_page_config(page_title="Scraper de Google Maps", layout="wide")

st.title("📍 Scraper de negocios en Google Maps")
st.markdown("Ingresa una búsqueda como: **'tienditas en Iztapalapa'**, **'dentistas en Guadalajara'**, etc.")

# Entrada del usuario
busqueda = st.text_input("🔎 Escribe tu búsqueda en Google Maps")

# Botón para activar scraping
if st.button("Buscar y extraer"):
    if not busqueda:
        st.warning("Escribe una búsqueda antes de continuar.")
    else:
        with st.spinner("Obteniendo resultados... esto puede tardar unos minutos."):
            try:
                df = scrapear_busqueda(busqueda)
                st.success(f"Se extrajeron {len(df)} resultados.")
                
                # Mostrar DataFrame
                st.dataframe(df)

                # Descargar en CSV
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Descargar resultados en CSV",
                    data=csv,
                    file_name=f"{busqueda.replace(' ', '_')}.csv",
                    mime="text/csv"
                )

            except Exception as e:
                st.error(f"❌ Error: {e}")