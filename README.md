# HangMan Adventure — Flask Edition

This project reuses the original HangMan Adventure HTML and CSS design. Flask (Python) handles word selection, difficulty rules, guesses, lives, and win/loss state. JavaScript connects the original interface to the Flask API.

## Four-step workflow
1. Welcome screen — click **Start Game**.
2. Category — choose Animals, Fruits, Vegetables, Countries, Sports, Technology, Flowers, or Vehicles.
3. Difficulty — choose Easy, Medium, Hard, or Expert.
4. Game — guess letters, view the hangman drawing and hint, and see the result.

The original colors, background, fonts, cards, buttons, animations, SVG hangman, responsive layout, sound toggle, settings toast, and game screens are retained. The visible step-counter labels have been removed.

## Run in VS Code (Windows)

1. Extract this ZIP file.
2. Open the `HangMan_Adventure_Flask` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Install the required package:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the Flask server:

   ```powershell
   python app.py
   ```

6. Open this address in your browser:

   `http://127.0.0.1:5000`

Keep the VS Code terminal open while playing. To stop the server, press `Ctrl + C` in the terminal.

If `python` is not recognized on your computer, try `py` in place of `python`.

## Project structure

```text
HangMan_Adventure_Flask/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## Notes
- Flask runs the game logic locally; JavaScript updates the browser interface.
- The Google Font is loaded from Google Fonts when internet access is available. A system font fallback is included.
- For public deployment, use a Python-capable host; GitHub Pages alone cannot run Flask.
