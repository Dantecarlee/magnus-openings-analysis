# Magnus Carlsen Opening Analysis

Analysis of Magnus Carlsen's (DrNykterstein) last 2000 Lichess games, exploring his win rate by opening depending on the color he plays.

## What it shows

For each combination of first and second move, the app displays:
- Number of wins, draws and losses
- Win%, Draw% and Lose%
- Average opponent ELO

## How to run

```bash
pip install streamlit requests pandas
streamlit run magnus_openings.py
```

Then open your browser at `http://localhost:8501`, select white or black and wait for the data to load (~1-2 minutes).

## Tech stack

- Python
- Lichess API
- pandas
- Streamlit

  ![App screenshot](Captura%20de%20pantalla%202026-05-28%20172438.png)
