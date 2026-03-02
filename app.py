import streamlit as st
import random

st.set_page_config(
    page_title="Hangman",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Word bank ──────────────────────────────────────────────────────────────────
WORD_BANK = {
    "Animals": [
        "elephant", "crocodile", "butterfly", "flamingo", "cheetah",
        "penguin", "gorilla", "dolphin", "porcupine", "mongoose",
        "chameleon", "albatross", "narwhal", "platypus", "wolverine",
    ],
    "Countries": [
        "brazil", "germany", "australia", "portugal", "indonesia",
        "argentina", "ethiopia", "cambodia", "switzerland", "madagascar",
        "luxembourg", "mozambique", "kyrgyzstan", "afghanistan", "venezuela",
    ],
    "Foods": [
        "avocado", "croissant", "blueberry", "spaghetti", "pineapple",
        "broccoli", "quesadilla", "eggplant", "cauliflower", "asparagus",
        "artichoke", "persimmon", "pomegranate", "bruschetta", "enchilada",
    ],
    "Sports": [
        "basketball", "volleyball", "badminton", "fencing", "lacrosse",
        "archery", "wrestling", "biathlon", "skateboard", "bobsleigh",
        "taekwondo", "gymnastics", "waterpolo", "powerlifting", "triathlon",
    ],
    "Technology": [
        "algorithm", "database", "framework", "compiler", "encryption",
        "blockchain", "javascript", "kubernetes", "raspberry", "tensorflow",
        "cybersecurity", "bandwidth", "hyperlink", "quantum", "microprocessor",
    ],
}

MAX_WRONG = 6

# ── SVG Hangman drawing ───────────────────────────────────────────────────────
def hangman_svg(wrong: int) -> str:
    parts = []
    # Gallows (always shown)
    gallows = """
      <line x1="20" y1="230" x2="180" y2="230" stroke="#94a3b8" stroke-width="4" stroke-linecap="round"/>
      <line x1="60" y1="230" x2="60" y2="20"  stroke="#94a3b8" stroke-width="4" stroke-linecap="round"/>
      <line x1="60" y1="20"  x2="130" y2="20" stroke="#94a3b8" stroke-width="4" stroke-linecap="round"/>
      <line x1="130" y1="20" x2="130" y2="45" stroke="#94a3b8" stroke-width="4" stroke-linecap="round"/>
    """
    # Body parts added per wrong guess
    body_parts = [
        # 1 – head
        '<circle cx="130" cy="65" r="20" stroke="#f97316" stroke-width="3" fill="none"/>',
        # 2 – body
        '<line x1="130" y1="85" x2="130" y2="145" stroke="#f97316" stroke-width="3" stroke-linecap="round"/>',
        # 3 – left arm
        '<line x1="130" y1="100" x2="100" y2="125" stroke="#f97316" stroke-width="3" stroke-linecap="round"/>',
        # 4 – right arm
        '<line x1="130" y1="100" x2="160" y2="125" stroke="#f97316" stroke-width="3" stroke-linecap="round"/>',
        # 5 – left leg
        '<line x1="130" y1="145" x2="100" y2="185" stroke="#f97316" stroke-width="3" stroke-linecap="round"/>',
        # 6 – right leg
        '<line x1="130" y1="145" x2="160" y2="185" stroke="#f97316" stroke-width="3" stroke-linecap="round"/>',
    ]
    for i in range(min(wrong, MAX_WRONG)):
        parts.append(body_parts[i])

    # Face when dead
    face = ""
    if wrong >= MAX_WRONG:
        face = """
          <line x1="122" y1="57" x2="126" y2="61" stroke="#ef4444" stroke-width="2"/>
          <line x1="126" y1="57" x2="122" y2="61" stroke="#ef4444" stroke-width="2"/>
          <line x1="134" y1="57" x2="138" y2="61" stroke="#ef4444" stroke-width="2"/>
          <line x1="138" y1="57" x2="134" y2="61" stroke="#ef4444" stroke-width="2"/>
          <path d="M122 74 Q130 68 138 74" stroke="#ef4444" stroke-width="2" fill="none"/>
        """
    elif wrong == 0:
        face = ""
    else:
        # Worried eyes
        face = """
          <circle cx="123" cy="60" r="3" fill="#f97316"/>
          <circle cx="137" cy="60" r="3" fill="#f97316"/>
        """

    return f"""
    <svg viewBox="0 0 200 245" xmlns="http://www.w3.org/2000/svg" width="200" height="245">
      {gallows}
      {"".join(parts)}
      {face}
    </svg>
    """

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    min-height: 100vh;
}

.game-title {
    text-align: center;
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(90deg, #f97316, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
    letter-spacing: -1px;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}

.card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.score-row {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin-bottom: 0.5rem;
}

.score-item {
    text-align: center;
}

.score-label {
    color: #94a3b8;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.score-value {
    font-size: 1.8rem;
    font-weight: 900;
    color: #f8fafc;
}

.score-value.wins { color: #22c55e; }
.score-value.losses { color: #ef4444; }
.score-value.streak { color: #f97316; }

.word-display {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    margin: 1rem 0;
}

.letter-box {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 50px;
    border-bottom: 3px solid #7c3aed;
    font-size: 1.6rem;
    font-weight: 800;
    color: #f8fafc;
    text-transform: uppercase;
    transition: all 0.3s ease;
}

.letter-box.revealed {
    color: #22c55e;
    border-bottom-color: #22c55e;
}

.letter-box.space {
    border-bottom: none;
    width: 20px;
}

.category-badge {
    display: inline-block;
    background: rgba(124, 58, 237, 0.3);
    border: 1px solid rgba(124, 58, 237, 0.5);
    color: #c4b5fd;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

.wrong-count {
    color: #ef4444;
    font-size: 0.95rem;
    font-weight: 700;
    text-align: center;
}

.hint-bar {
    height: 8px;
    border-radius: 4px;
    background: #1e293b;
    overflow: hidden;
    margin: 6px 0;
}

.hint-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
}

.result-win {
    text-align: center;
    font-size: 2rem;
    font-weight: 900;
    color: #22c55e;
    padding: 0.5rem;
    animation: pulse 1s infinite;
}

.result-lose {
    text-align: center;
    font-size: 1.5rem;
    font-weight: 900;
    color: #ef4444;
    padding: 0.5rem;
}

.answer-reveal {
    text-align: center;
    font-size: 1.2rem;
    color: #f97316;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-top: 0.3rem;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

.svg-container {
    display: flex;
    justify-content: center;
    margin: 0.5rem 0;
}

.keyboard-row {
    display: flex;
    justify-content: center;
    gap: 5px;
    margin-bottom: 5px;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
def init_state():
    if "word" not in st.session_state:
        st.session_state.word = ""
    if "category" not in st.session_state:
        st.session_state.category = ""
    if "guessed" not in st.session_state:
        st.session_state.guessed = set()
    if "wins" not in st.session_state:
        st.session_state.wins = 0
    if "losses" not in st.session_state:
        st.session_state.losses = 0
    if "streak" not in st.session_state:
        st.session_state.streak = 0
    if "game_over" not in st.session_state:
        st.session_state.game_over = False
    if "won" not in st.session_state:
        st.session_state.won = False

def new_game(category=None):
    if category and category in WORD_BANK:
        cat = category
    else:
        cat = random.choice(list(WORD_BANK.keys()))
    word = random.choice(WORD_BANK[cat])
    st.session_state.word = word
    st.session_state.category = cat
    st.session_state.guessed = set()
    st.session_state.game_over = False
    st.session_state.won = False

init_state()
if not st.session_state.word:
    new_game()

word = st.session_state.word
guessed = st.session_state.guessed
wrong_letters = [l for l in guessed if l not in word]
wrong_count = len(wrong_letters)

# Check win/lose
all_revealed = all(c in guessed for c in word)
if all_revealed and not st.session_state.game_over:
    st.session_state.game_over = True
    st.session_state.won = True
    st.session_state.wins += 1
    st.session_state.streak += 1
elif wrong_count >= MAX_WRONG and not st.session_state.game_over:
    st.session_state.game_over = True
    st.session_state.won = False
    st.session_state.losses += 1
    st.session_state.streak = 0

# ── Render ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="game-title">🎯 Hangman</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Guess the word before the figure is complete!</div>', unsafe_allow_html=True)

# Scoreboard
st.markdown(f"""
<div class="card">
  <div class="score-row">
    <div class="score-item">
      <div class="score-label">Wins</div>
      <div class="score-value wins">{st.session_state.wins}</div>
    </div>
    <div class="score-item">
      <div class="score-label">Losses</div>
      <div class="score-value losses">{st.session_state.losses}</div>
    </div>
    <div class="score-item">
      <div class="score-label">Streak 🔥</div>
      <div class="score-value streak">{st.session_state.streak}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Category badge + SVG + Word + Progress
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown(f'<div class="svg-container">{hangman_svg(wrong_count)}</div>', unsafe_allow_html=True)

    # Danger bar
    pct = int((wrong_count / MAX_WRONG) * 100)
    if pct < 40:
        bar_color = "#22c55e"
    elif pct < 70:
        bar_color = "#f97316"
    else:
        bar_color = "#ef4444"
    st.markdown(f"""
    <div style="text-align:center;">
      <div class="wrong-count">{wrong_count} / {MAX_WRONG} wrong</div>
      <div class="hint-bar">
        <div class="hint-fill" style="width:{pct}%; background:{bar_color};"></div>
      </div>
      <div style="color:#94a3b8;font-size:0.8rem;">
        Wrong: {', '.join(sorted(wrong_letters)).upper() if wrong_letters else '—'}
      </div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown(f'<div style="text-align:center;"><span class="category-badge">📚 {st.session_state.category}</span></div>', unsafe_allow_html=True)

    # Word display
    boxes = ""
    for c in word:
        if c == " ":
            boxes += '<span class="letter-box space">&nbsp;</span>'
        elif c in guessed or st.session_state.game_over:
            cls = "letter-box revealed" if c in guessed else "letter-box"
            boxes += f'<span class="{cls}">{c}</span>'
        else:
            boxes += '<span class="letter-box">_</span>'
    st.markdown(f'<div class="word-display">{boxes}</div>', unsafe_allow_html=True)

    # Result message
    if st.session_state.game_over:
        if st.session_state.won:
            st.markdown('<div class="result-win">🎉 YOU WIN!</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="result-lose">💀 GAME OVER</div><div class="answer-reveal">{word}</div>', unsafe_allow_html=True)
    else:
        letters_left = sum(1 for c in set(word) if c != " " and c not in guessed)
        st.markdown(f'<div style="text-align:center;color:#94a3b8;font-size:0.85rem;margin-top:0.5rem;">{letters_left} unique letter{"s" if letters_left != 1 else ""} remaining</div>', unsafe_allow_html=True)

# ── Keyboard ──────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

if not st.session_state.game_over:
    rows = [
        list("qwertyuiop"),
        list("asdfghjkl"),
        list("zxcvbnm"),
    ]
    for row in rows:
        cols = st.columns(len(row))
        for i, letter in enumerate(row):
            with cols[i]:
                already_guessed = letter in guessed
                correct = letter in word
                if already_guessed:
                    label = f"~~{letter.upper()}~~" if not correct else f"**{letter.upper()}**"
                    btn_type = "secondary"
                else:
                    label = letter.upper()
                    btn_type = "primary"
                disabled = already_guessed
                if st.button(label, key=f"key_{letter}", disabled=disabled, use_container_width=True, type=btn_type):
                    st.session_state.guessed.add(letter)
                    st.rerun()

# ── Controls ───────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
ctrl_cols = st.columns([1, 1, 1])

with ctrl_cols[0]:
    if st.button("🔄 New Game", use_container_width=True, type="primary"):
        new_game()
        st.rerun()

with ctrl_cols[1]:
    cat = st.selectbox(
        "Category",
        options=["Random"] + list(WORD_BANK.keys()),
        label_visibility="collapsed",
    )

with ctrl_cols[2]:
    if st.button("▶ Play Category", use_container_width=True):
        new_game(None if cat == "Random" else cat)
        st.rerun()

st.markdown('<div style="text-align:center;color:#334155;font-size:0.75rem;margin-top:2rem;">Hangman · Built with Streamlit · Kolossus</div>', unsafe_allow_html=True)
