import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# ----------------------------------------------
# 1. GENERAR DATASET DE EJEMPLO (si no existe)
# ----------------------------------------------
DATA_PATH = "data/juegos.csv"

if not os.path.exists(DATA_PATH):
    os.makedirs("data", exist_ok=True)
    
    # Dataset de ejemplo con juegos reales de Steam (simplificado)
    sample_data = {
        "nombre": [
            "The Witcher 3", "Cyberpunk 2077", "Stardew Valley", "Hades",
            "Baldur's Gate 3", "Elden Ring", "Minecraft", "Terraria",
            "Counter-Strike 2", "Dota 2", "Among Us", "Valorant"
        ],
        "genero": [
            "RPG", "RPG", "Simulación", "Roguelike",
            "RPG", "RPG", "Aventura", "Aventura",
            "FPS", "MOBA", "Party", "FPS"
        ],
        "rating": [
            96, 75, 89, 94,
            97, 95, 88, 87,
            82, 85, 79, 84
        ],
        "precio_usd": [
            30, 60, 15, 25,
            60, 60, 27, 10,
            0, 0, 5, 0
        ],
        "plataforma": [
            "PC,PS4", "PC,PS5,Xbox", "PC,Switch", "PC,Switch",
            "PC,PS5", "PC,PS5,Xbox", "PC,Android", "PC,Switch",
            "PC", "PC", "PC,Android", "PC"
        ]
    }
    df_sample = pd.DataFrame(sample_data)
    df_sample.to_csv(DATA_PATH, index=False)
    st.success(f"✅ Dataset de ejemplo creado en {DATA_PATH}")

# ----------------------------------------------
# 2. CARGAR DATOS CON PANDAS
# ----------------------------------------------
@st.cache_data
def cargar_datos():
    return pd.read_csv(DATA_PATH)

df = cargar_datos()

# ----------------------------------------------
# 3. SISTEMA DE SCORING (lógica propia)
# ----------------------------------------------
def calcular_score(juego, genero_pref, rating_min, max_precio):
    score = 0
    
    # 1. Match de género (peso alto)
    if juego["genero"] == genero_pref:
        score += 10
    
    # 2. Rating: cuanto más alto, mejor (0 a 10 puntos)
    rating = juego["rating"]
    score += (rating / 100) * 10   # Normalizamos a 10
    
    # 3. Precio: si es gratis o muy barato suma
    if juego["precio_usd"] == 0:
        score += 3
    elif juego["precio_usd"] <= max_precio:
        score += 2
    else:
        score -= 2   # penaliza si supera el presupuesto
    
    return round(score, 2)

# ----------------------------------------------
# 4. INTERFAZ CON STREAMLIT
# ----------------------------------------------
st.set_page_config(page_title="Recomendador de Juegos", layout="wide")
st.title("🎮 Recomendador de Juegos (Steam)")
st.markdown("Encontrá tu próximo juego favorito según **género**, **rating** y **presupuesto**.")

# Sidebar con filtros
st.sidebar.header("🔍 Tus preferencias")
genero_elegido = st.sidebar.selectbox("🎭 Género", options=sorted(df["genero"].unique()))
rating_minimo = st.sidebar.slider("⭐ Rating mínimo (0-100)", 0, 100, 70)
precio_maximo = st.sidebar.number_input("💰 Precio máximo (USD)", min_value=0, value=30, step=5)
top_n = st.sidebar.slider("🏆 Cantidad de recomendaciones", 1, 10, 5)

# Botón de recomendar
if st.sidebar.button("🎯 Recomendar juegos"):
    # Aplicar filtros básicos (rating y precio)
    filtrados = df[(df["rating"] >= rating_minimo) & (df["precio_usd"] <= precio_maximo)].copy()
    
    if filtrados.empty:
        st.warning("😕 No hay juegos que cumplan con esos filtros. Probá con rating más bajo o mayor presupuesto.")
    else:
        # Calcular score para cada juego filtrado
        filtrados["score"] = filtrados.apply(
            lambda row: calcular_score(row, genero_elegido, rating_minimo, precio_maximo),
            axis=1
        )
        
        # Ordenar por score y mostrar top N
        recomendados = filtrados.sort_values("score", ascending=False).head(top_n)
        
        st.subheader(f"🔥 Top {top_n} juegos recomendados para {genero_elegido}")
        
        for idx, row in recomendados.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.markdown(f"**{row['nombre']}**")
                col2.markdown(f"⭐ {row['rating']}")
                col3.markdown(f"💵 ${row['precio_usd']}")
                st.markdown(f"*Género:* {row['genero']}  |  *Plataforma:* {row['plataforma']}  |  *Score personalizado:* {row['score']}")
                st.divider()
        
        # Gráfico opcional con Matplotlib
        st.subheader("📊 Comparativa de rating de los recomendados")
        fig, ax = plt.subplots()
        ax.barh(recomendados["nombre"], recomendados["rating"], color="skyblue")
        ax.set_xlabel("Rating")
        ax.set_title("Rating de los juegos sugeridos")
        st.pyplot(fig)

# Mostrar dataset completo si el usuario quiere explorar
with st.expander("📂 Ver dataset completo"):
    st.dataframe(df)
