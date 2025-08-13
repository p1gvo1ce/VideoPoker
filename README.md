🎰 Video Poker (Kivy Edition)

A classic Video Poker game built with Python and Kivy.Cards, chips, combinations, payout logic — all wrapped in a slick interface with custom graphics and animations.

![Screenshot](assets/screenshots/demo.png)

---

🕹 Features

🎴 Custom card deck with smooth delayed reveal animation

💸 Fully configurable bets (chip value + quantity)

📈 Payout table with visual highlighting of winning combos

💡 HOLD system with toggles

🟨 Blinking row effect on win

🎯 Accurate hand evaluation (Jacks or Better rules)

🔒 Fairness system with cryptographic seed commitment

Commitment (SHA-256 of server seed) shown before dealing

Seed revealed after replace phase

Full-deck order reproducible in control app

Deterministic shuffle via Fisher–Yates + NumPy PCG64 + SeedSequence(sha256(seed)->uint32[8])

📤 Manual seed-check mode (main_check):

Enter a known seed to reproduce the exact shuffle

View full deck order

HOLD + REPLACE work as in live mode

🧾 Credit system with grace & fee

Take credit in fixed chunks (e.g., +100) any number of times

Grace applies to the latest credit for the next hand only

1% fee per played hand on outstanding debt excluding the grace-covered portion (rounded up to whole chips, min 1)

Fee is capitalized into the debt; repayment is full when balance covers the debt

📦 Installation

Clone the repo:

git clone https://github.com/yourname/video-poker-kivy.git
cd video-poker-kivy

Create and activate virtual environment:

python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

Install dependencies:

pip install -r requirements.txt

Run:

python main.py

🧱 Project Structure

.
├── main.py              # Entry point
├── main_logic.py        # Game logic and mechanics
├── pokergame.kv         # Kivy layout and UI rules
├── dealer.py            # Card dealing and evaluation logic
├── deck_manager.py      # Card/rank/suit definitions
├── assets/
│   └── combinations/    # Visuals for poker hands
├── cards/               # All card images
└── README.md

🎨 Assets

Card backs and faces: custom or open-license sources (Wikimedia, OpenGameArt).Easily replaceable via the cards/ folder.

🛠 To-Do

Touch support optimization for mobile

Save/load player balance

Royal flush bonus animation

🔍 Fairness Verification

At deal time — the game shows the SHA-256 hash of the secret server seed (commitment).

After replace phase — the game reveals the seed.

Verification (control app):

h = sha256(seed.encode()).digest()
ss = SeedSequence(np.frombuffer(h, dtype=np.uint32))
rng = Generator(PCG64(ss))
Fisher–Yates shuffle over a standard 52-card deck

Compare the first 5 + replaced cards with the played hand. Any player can confirm the deck order matched the committed seed — no hidden rigging possible.

💳 Credit & Grace Mechanics

The game includes a simple, transparent loan system designed to prevent abuse while keeping play fluid.

Taking credit

Press Get Credit +100 to add 100 chips to your balance.This increases Outstanding Debt and Total Credit Taken by the same amount.

You may take credit multiple times in a row.

Each new credit grants a grace amount equal to that credit, valid for the next hand only.

Fee (1% per played hand)

Before each new played hand, a fee of 1% is applied to the portion of debt not covered by grace.Formula: fee = ceil(max(0, debt - grace) * 0.01) with a minimum of 1 chip.

No fee is charged if the current grace fully covers the debt (or if debt is zero).

The fee is capitalized into the debt (added to Outstanding Debt). If balance covers the fee, it is deducted from the balance; otherwise, only the debt increases.

After the fee is processed, the grace amount expires (used for that single hand).

Repayment

Repay becomes available when your balance ≥ outstanding debt.

Repayment clears the entire outstanding debt in one action (full repayment).

Examples

Debt = 500, Grace = 100 → fee on next hand = ceil((500-100)*1%) = ceil(4) = 4.

Debt = 80, Grace = 100 → fee = 0 (grace fully covers the debt for that hand). Grace then expires.

Take credit twice (+100 then +100):

After the first: Grace = 100 (applies to next hand)

If you take another +100 before playing, Grace becomes 200 (covers the combined newly taken amount).

Fee still applies to any older debt beyond this grace.

