import requests
import json
import pandas as pd
import streamlit as st

url = "https://lichess.org/api/games/user/DrNykterstein"  # Magnus Carlsen

headers = {
    "Accept": "application/x-ndjson"
}

color = st.selectbox("Seleccionar color", ["White", "Black"])


def opuesto(color):
    if color == "white":
        return "black"
    else: return "white"

params = {
    "max": 2000,
    "moves": True,
    "ratings": True,
    "color" : color
}

response = requests.get(url, headers=headers, params=params)
lines = response.text.split("\n")

data = []

def primer_mov(game):
    moves = game.get("moves", "")
    if len(moves) == 0:
        return ""
    else: return moves.split()[0]
    
def segundo_mov(game):
    moves = game.get("moves", "")
    movs = moves.split()
    if len(movs) < 2:
        return ""
    return movs[1]

for line in lines:
    if line.strip() == "":
        continue
    game = json.loads(line)
    if primer_mov(game) == "" or segundo_mov(game) == "":
        continue
    opp_rating = game["players"][opuesto(color)].get("rating", 0)
    winner = game.get("winner")
    data.append({
    "first_move": primer_mov(game),
    "opp_rating": opp_rating,
    "winner": winner,
    "second_move": segundo_mov(game)
})

df = pd.DataFrame(data)
df["winner"] = df["winner"].fillna("draw")
df = df[df["opp_rating"] > 0] 

win_opening = df.groupby(["first_move", "second_move"])["winner"].value_counts().unstack().fillna(0).astype(int)
win_opening = win_opening.rename(columns={"white": "White", "black": "Black", "draw": "Draw"})
win_opening["Total"] = win_opening.sum(axis=1)
win_opening["Win%"] = (win_opening[color.capitalize()] / win_opening["Total"]).round(2)*100
win_opening["Draw%"] = (win_opening["Draw"] / win_opening["Total"]).round(2)*100
win_opening["Lose%"] = (win_opening[opuesto(color).capitalize()] / win_opening["Total"]).round(2)*100
win_opening = win_opening.sort_values("Win%", ascending=False)
win_opening = win_opening[win_opening["Total"] >= 10]
win_opening["Opponent ELO Avg"] = df.groupby(["first_move", "second_move"])["opp_rating"].mean().round(2)
win_opening.index.names = ["First Move", "Second Move"]
                                 
st.dataframe(win_opening)