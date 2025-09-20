import streamlit as st
import numpy as np
import plotly.graph_objects as go
from st_keyup import st_keyup
from streamlit.components.v1 import html

# --- 1. Page Config ---
st.set_page_config(layout="wide")
st.title("🧩 3D Maze Game")

# --- 2. Game Settings ---
MAZE_SIZE = 10  # 미로의 크기

# --- 3. Core Functions ---

def initialize_game():
    """Generates a new maze and resets the game state."""
    maze = np.random.choice([0, 1], size=(MAZE_SIZE, MAZE_SIZE, MAZE_SIZE), p=[0.7, 0.3])
    
    # Ensure start and end points are always open paths
    start_pos = [0, 0, 0]
    end_pos = [MAZE_SIZE - 1, MAZE_SIZE - 1, MAZE_SIZE - 1]
    maze[tuple(start_pos)] = 0
    maze[tuple(end_pos)] = 0

    st.session_state.maze = maze
    st.session_state.player_pos = start_pos
    st.session_state.end_pos = end_pos
    st.session_state.message = "미로의 끝에 도달하세요!"

@st.cache_data
def get_cached_wall_trace(_maze_tuple):
    """Caches the 3D data for the maze walls to improve performance."""
    maze_array = np.array(_maze_tuple)
    z, y, x = np.where(maze_array == 1)
    
    wall_trace = go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(color='grey', size=5, symbol='square', opacity=0.6),
        name='벽'
    )
    return wall_trace

def create_maze_figure():
    """Creates the 3D plot of the maze using cached walls."""
    maze = st.session_state.maze
    player_pos = st.session_state.player_pos
    end_pos = st.session_state.end_pos

    maze_tuple = tuple(map(tuple, maze))
    wall_trace = get_cached_wall_trace(maze_tuple)
    
    fig = go.Figure(data=[wall_trace])

    # Add player and end point markers (these are not cached)
    fig.add_trace(go.Scatter3d(
        x=[player_pos[2]], y=[player_pos[1]], z=[player_pos[0]],
        mode='markers', marker=dict(color='red', size=10, symbol='circle'), name='플레이어'
    ))
    fig.add_trace(go.Scatter3d(
        x=[end_pos[2]], y=[end_pos[1]], z=[end_pos[0]],
        mode='markers', marker=dict(color='green', size=10, symbol='diamond'), name='도착'
    ))

    fig.update_layout(
        title="3D 미로",
        scene=dict(
            xaxis=dict(range=[-1, MAZE_SIZE]),
            yaxis=dict(range=[-1, MAZE_SIZE]),
            zaxis=dict(range=[-1, MAZE_SIZE]),
            aspectratio=dict(x=1, y=1, z=1),
            camera_eye=dict(x=1.5, y=1.5, z=1.5)
        ),
        margin=dict(l=0, r=0, b=0, t=40)
    )
    return fig

def move_player(dz, dy, dx):
    """Handles player movement logic."""
    new_pos = [
        st.session_state.player_pos[0] + dz,
        st.session_state.player_pos[1] + dy,
        st.session_state.player_pos[2] + dx,
    ]

    if not (0 <= new_pos[0] < MAZE_SIZE and 0 <= new_pos[1] < MAZE_SIZE and 0 <= new_pos[2] < MAZE_SIZE):
        st.session_state.message = "미로의 끝입니다! 🚧"; return
    if st.session_state.maze[tuple(new_pos)] == 1:
        st.session_state.message = "그곳은 벽입니다! 🧱"; return
    
    st.session_state.player_pos = new_pos
    st.session_state.message = "계속 움직이세요!"

    if new_pos == st.session_state.end_pos:
        st.session_state.message = "🎉 탈출 성공! 🎉"; st.balloons()

def autofocus_keyup():
    """Automatically focuses the key input box using JavaScript for continuous play."""
    html(
        f"""
        <script>
            setTimeout(function() {{
                var input = window.parent.document.querySelector("input[aria-label='{st.session_state.keyup_label}']");
                if (input) {{
                    input.focus();
                }}
            }}, 200);
        </script>
        """,
        height=0, width=0
    )

# --- 4. Game Initialization ---
if 'maze' not in st.session_state:
    initialize_game()

# --- 5. Main Layout and Rendering ---
col1, col2 = st.columns([3, 1])

with col1:
    st.plotly_chart(create_maze_figure(), use_container_width=True, key="maze_chart")

with col2:
    st.subheader("🕹️ 컨트롤러")
    st.info("이제 마우스 클릭 없이 키보드로 연속 조종이 가능합니다!")
    st.write(f"현재 위치: {st.session_state.player_pos}")
    st.warning(st.session_state.message)

    st.session_state.keyup_label = "여기를 클릭하여 시작"
    key = st_keyup(st.session_state.keyup_label, debounce=200, key="maze_controller")
    
    st.write("---")
    st.markdown("""
    - **W / ↑**: 북쪽
    - **S / ↓**: 남쪽
    - **A / ←**: 서쪽
    - **D / →**: 동쪽
    - **E**: 위로 (Up)
    - **Q**: 아래로 (Down)
    """)
    st.write("---")

    if key:
        if key.lower() == 'e': move_player(1, 0, 0)
        elif key.lower() == 'q': move_player(-1, 0, 0)
        elif key.lower() == 'w' or key == 'ArrowUp': move_player(0, 1, 0)
        elif key.lower() == 's' or key == 'ArrowDown': move_player(0, -1, 0)
        elif key.lower() == 'd' or key == 'ArrowRight': move_player(0, 0, 1)
        elif key.lower() == 'a' or key == 'ArrowLeft': move_player(0, 0, -1)
        
        # Clear the key value to prevent infinite loop
        st.session_state.maze_controller = "" 
        st.rerun()

    st.divider()
    if st.button("새로운 미로 생성"):
        initialize_game()
        st.rerun()

    # Call the autofocus function at the end of each run
    autofocus_keyup()
