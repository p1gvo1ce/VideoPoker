# 🎰 Video Poker (Kivy Edition)

A classic **Video Poker** game built with Python and Kivy.  
Cards, chips, combinations, payout logic — all wrapped in a slick interface with custom graphics and animations.

![Screenshot](assets/screenshots/demo.png)

---

## 🕹 Features

- 🎴 **Custom card deck** with smooth delayed reveal animation
- 💸 Fully configurable bets (chip value + quantity)
- 📈 Payout table with visual highlighting of winning combos
- 💡 HOLD system with toggles
- 🟨 Blinking row effect on win
- 🎯 Accurate hand evaluation (Jacks or Better rules)

- 🔒 **Fairness system with cryptographic seed commitment**
  - Commitment (SHA-256 of server seed) shown **before** dealing
  - Seed revealed **after** replace phase
  - Full-deck order reproducible in control app
  - Deterministic shuffle via Fisher–Yates + NumPy `PCG64` + `SeedSequence(sha256(seed)->uint32[8])`
- 📤 **Manual seed-check mode** (`main_check`):
  - Enter a known seed to reproduce the exact shuffle
  - View full deck order
  - HOLD + REPLACE work as in live mode

---

## 📦 Installation

1. Clone the repo:

```bash
git clone https://github.com/yourname/video-poker-kivy.git
cd video-poker-kivy
```
Create and activate virtual environment:
```
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```
Install dependencies:
```
pip install -r requirements.txt
```
Run:
```
python main.py
```
🧱 Project Structure
```
.
├── main.py              # Entry point
├── main_logic.py        # Game logic and mechanics
├── pokergame.kv         # Kivy layout and UI rules
├── dealer.py            # Card dealing and evaluation logic
├── assets/
│   └── combinations/    # Visuals for poker hands
├── cards/               # All card images
└── README.md
```
🎨 Assets

    Card backs and faces: custom or open-license sources (Wikimedia, OpenGameArt)

    Easily replaceable via cards/ folder

🛠 To-Do

    Sound effects for dealing & winning

    Touch support optimization for mobile

    Save/load player balance

    Royal flush bonus animation

🔍 Fairness Verification

    At deal time — the game shows SHA-256 hash of the secret server seed (commitment).

    After replace phase — the game reveals the seed.

    Verification:

        Control app applies the same shuffle algorithm:

        h = sha256(seed.encode()).digest()
        ss = SeedSequence(np.frombuffer(h, dtype=np.uint32))
        rng = Generator(PCG64(ss))
        Fisher–Yates shuffle over a standard 52-card deck

        Compare first 5 + replaced cards with the played hand.

Any player can confirm the deck order matched the committed seed — no hidden rigging possible.