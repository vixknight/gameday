# Game Day NPV Calculator

A small Streamlit app that compares:

- The net present value of watching a Yankees game from behind home plate
- The net present value of playing soccer with friends

The calculation responds to three sliders:

1. Chance of rain
2. Expected fun of the Yankees game
3. Expected fun of playing soccer

Values are displayed using a red-yellow-green heatmap scale.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy from GitHub

1. Create a GitHub repository.
2. Upload `app.py` and `requirements.txt`.
3. Sign in to Streamlit Community Cloud.
4. Choose **Create app**.
5. Select the repository and set the main file path to `app.py`.

Note: GitHub Pages cannot execute Python applications directly. The GitHub repository stores the code, while Streamlit Community Cloud runs the app.
