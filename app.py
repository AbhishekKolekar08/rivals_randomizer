import streamlit as st
import random
import time

# ===============================
# LOAD DEFAULTS FROM SECRETS
# ===============================
DEFAULT_PLAYERS = st.secrets["players"]["default"]
DEFAULT_CHARACTERS = st.secrets["characters"]["default"]
APP_TITLE = st.secrets.get("general", {}).get("app_name", "Marvel Rivals Randomizer")

# ===============================
# SESSION STATE INIT
# ===============================
if "players" not in st.session_state:
    st.session_state.players = DEFAULT_PLAYERS.copy()
if "temp_players" not in st.session_state:
    st.session_state.temp_players = []  # session-only additions
if "player_checks" not in st.session_state:
    st.session_state.player_checks = {p: False for p in st.session_state.players}
if "assignments" not in st.session_state:
    st.session_state.assignments = None
if "characters" not in st.session_state:
    st.session_state.characters = DEFAULT_CHARACTERS.copy()

# keep checkbox dict in sync
for p in st.session_state.players + st.session_state.temp_players:
    st.session_state.player_checks.setdefault(p, False)
for p in list(st.session_state.player_checks.keys()):
    if p not in st.session_state.players + st.session_state.temp_players:
        del st.session_state.player_checks[p]

players = st.session_state.players + st.session_state.temp_players
characters = st.session_state.characters

# ===============================
# PAGE LAYOUT
# ===============================
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)

# three columns: left UI, spacer, right UI
col1, spacer, col2 = st.columns([1, 0.08, 2])

# -------------------------------
# LEFT COLUMN: PLAYERS
# -------------------------------
with col1:
    st.subheader("Players")
    st.write("Select players:")

    left_col, right_col = st.columns(2)
    half = (len(players) + 1) // 2
    left_players = players[:half]
    right_players = players[half:]

    with left_col:
        for name in left_players:
            key = f"cb_left_{name}"
            st.session_state.player_checks[name] = st.checkbox(
                name,
                value=st.session_state.player_checks.get(name, False),
                key=key,
            )

    with right_col:
        for name in right_players:
            key = f"cb_right_{name}"
            st.session_state.player_checks[name] = st.checkbox(
                name,
                value=st.session_state.player_checks.get(name, False),
                key=key,
            )

    # st.divider()
    # st.info(f"Persistent players: {len(st.session_state.players)} • Temporary this session: {len(st.session_state.temp_players)}")
    # st.divider()

    # Add player area
    st.subheader("Add Player")
    new_player = st.text_input("Enter player name:", key="add_player_input")

    col_add_temp = st.columns(1)[0]

    with col_add_temp:
        if st.button("Add Temporary Player", use_container_width=True):
            name = new_player.strip()
            if len(name) < 2:
                st.error("Name too short (min 2 characters).")
            elif name in players:
                st.error("Player already exists.")
            else:
                st.session_state.temp_players.append(name)
                st.session_state.player_checks[name] = True
                st.success(f"Added temporary player for this session: {name}")
                st.stop()  # <- replaces experimental_rerun

    st.caption("Temporary players exist only for this browser session; they vanish when the app restarts.")
    st.caption(f"Characters available: {len(characters)}")

# spacer
with spacer:
    st.write("")

# -------------------------------
# RIGHT COLUMN: INSTRUCTIONS + ASSIGNMENTS
# -------------------------------
with col2:
    st.subheader("Instructions")
    st.markdown(
        "1. Tick the players on the left.\n"
        "2. Click **Assign Characters**.\n"
        "3. Temporary players are session-only."
    )

    if st.button("Assign Characters", use_container_width=True, type="primary"):
        chosen = [p for p, v in st.session_state.player_checks.items() if v]
        if not chosen:
            st.error("No players selected.")
        elif len(chosen) > len(characters):
            st.error(f"Not enough unique characters (need {len(chosen)}, have {len(characters)}).")
        else:
            with st.spinner("Randomizing assignments..."):
                time.sleep(0.5)
                pool = characters.copy()
                random.shuffle(pool)
                st.session_state.assignments = {p: pool.pop() for p in chosen}

    st.subheader("Results")
    if st.session_state.assignments:
        lines = [
            f"{i}. {player}: {char}"
            for i, (player, char) in enumerate(st.session_state.assignments.items(), 1)
        ]
        html = "<br>".join(lines)
        st.markdown(
            f"""
            <div style="font-size:20px; font-weight:600; line-height:1.6;">
                {html}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("No assignments yet. Select players and click Assign Characters.")
