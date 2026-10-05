import json

import pandas as pd
import requests
import streamlit as st

URL = "https://lichess.org/api/games/user/DrNykterstein"  # Magnus Carlsen
MAX_PARTIDAS = 2000
MIN_PARTIDAS = 10  # mínimo de partidas por apertura para mostrarla


def opuesto(color: str) -> str:
    """Devuelve el color contrario. Espera 'white' o 'black' en minúscula."""
    return "black" if color == "white" else "white"


@st.cache_data(show_spinner="Descargando partidas de Lichess...", ttl=3600)
def descargar_partidas(color: str) -> list[dict]:
    """Descarga las últimas partidas de Magnus jugando con el color dado."""
    params = {
        "max": MAX_PARTIDAS,
        "moves": True,
        "ratings": True,
        "color": color,
    }
    headers = {"Accept": "application/x-ndjson"}
    response = requests.get(URL, headers=headers, params=params, timeout=120)
    response.raise_for_status()
    return [json.loads(linea) for linea in response.text.splitlines() if linea.strip()]


def primeros_movimientos(game: dict) -> tuple[str, str]:
    """Devuelve (primer movimiento, segundo movimiento), o ('', '') si no hay suficientes."""
    movs = game.get("moves", "").split()
    if len(movs) < 2:
        return "", ""
    return movs[0], movs[1]


def armar_dataframe(partidas: list[dict], color: str) -> pd.DataFrame:
    """Arma una fila por partida con la apertura, el rating del rival y el resultado."""
    filas = []
    for game in partidas:
        primero, segundo = primeros_movimientos(game)
        if not primero:
            continue
        rating_rival = game["players"][opuesto(color)].get("rating", 0)
        if rating_rival <= 0:
            continue
        filas.append({
            "first_move": primero,
            "second_move": segundo,
            "opp_rating": rating_rival,
            "winner": game.get("winner", "draw"),  # sin ganador = tablas
        })
    return pd.DataFrame(filas)


def calcular_estadisticas(df: pd.DataFrame, color: str) -> pd.DataFrame:
    """Victorias, tablas y derrotas de Magnus por primeros dos movimientos."""
    df = df.copy()
    df["resultado"] = df["winner"].map(
        lambda ganador: "Win" if ganador == color else ("Draw" if ganador == "draw" else "Loss")
    )

    stats = (
        pd.crosstab([df["first_move"], df["second_move"]], df["resultado"])
        .reindex(columns=["Win", "Draw", "Loss"], fill_value=0)
    )
    stats["Total"] = stats.sum(axis=1)
    for columna in ["Win", "Draw", "Loss"]:
        stats[f"{columna}%"] = (stats[columna] / stats["Total"] * 100).round(1)

    elo_promedio = df.groupby(["first_move", "second_move"])["opp_rating"].mean().round(0)
    stats["Opponent ELO Avg"] = elo_promedio

    stats = stats[stats["Total"] >= MIN_PARTIDAS]
    stats = stats.sort_values("Win%", ascending=False)
    stats.index.names = ["First Move", "Second Move"]
    return stats


def main() -> None:
    color_elegido = st.selectbox("Seleccionar color", ["White", "Black"])
    color = color_elegido.lower()  # la API de Lichess espera 'white' o 'black'

    try:
        partidas = descargar_partidas(color)
    except requests.RequestException as error:
        st.error(f"No se pudieron descargar las partidas de Lichess: {error}")
        st.stop()

    df = armar_dataframe(partidas, color)
    if df.empty:
        st.warning("No se encontraron partidas para analizar.")
        st.stop()

    stats = calcular_estadisticas(df, color)
    if stats.empty:
        st.info(f"Ninguna apertura tiene al menos {MIN_PARTIDAS} partidas.")
        st.stop()

    st.dataframe(stats)


if __name__ == "__main__":
    main()
