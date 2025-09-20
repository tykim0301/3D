import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- 페이지 설정 ---
st.set_page_config(layout="wide")
st.title("🧩 3D 미로 구현ㄷㄷ")

# --- 게임 설정 ---
MAZE_SIZE = 10  # 미로의 크기 (5x5x5)

# --- 게임 상태 초기화 (Session State) ---
# --- 기존 initialize_game 함수를 아래의 올바른 코드로 통째로 교체해주세요 ---

def initialize_game():
    # 3D 미로 생성 (0: 길, 1: 벽)
    # 아래 라인의 오타를 수정했습니다.
    maze = np.random.choice([0, 1], size=(MAZE_SIZE, MAZE_SIZE, MAZE_SIZE), p=[0.7, 0.3])
    
    # 시작점과 끝점은 항상 길로 만듦
    start_pos = [0, 0, 0]
    end_pos = [MAZE_SIZE - 1, MAZE_SIZE - 1, MAZE_SIZE - 1]
    maze[tuple(start_pos)] = 0
    maze[tuple(end_pos)] = 0

    st.session_state.maze = maze
    st.session_state.player_pos = start_pos
    st.session_state.end_pos = end_pos
    st.session_state.message = "미로의 끝에 도달하세요!"

    # --- 이 함수 전체를 복사해서 `create_maze_figure` 함수보다 **위에** 붙여넣어 주세요 ---

@st.cache_data
def get_cached_wall_trace(_maze_tuple):
    """미로의 벽 부분만 3D 데이터로 변환하고, 그 결과를 캐시에 저장합니다."""
    maze_array = np.array(_maze_tuple) # 튜플을 다시 numpy 배열로 변환
    z, y, x = np.where(maze_array == 1)
    
    wall_trace = go.Scatter3d(
        x=x, y=y, z=z,
        mode='markers',
        marker=dict(
            color='grey',
            size=5,
            symbol='square',
            opacity=0.6
        ),
        name='벽'
    )
    return wall_trace

# session_state에 게임이 없으면 초기화
if 'maze' not in st.session_state:
    initialize_game()

# --- 3D 미로 시각화 함수 (수정된 버전) ---
# --- 기존 create_maze_figure 함수를 아래 코드로 교체 ---

def create_maze_figure():
    maze = st.session_state.maze
    player_pos = st.session_state.player_pos
    end_pos = st.session_state.end_pos

    # 1. 캐시된 벽 데이터를 불러오기
    # Numpy 배열은 캐시할 수 없으므로, 해시 가능한 튜플로 변환해서 전달
    maze_tuple = tuple(map(tuple, maze))
    wall_trace = get_cached_wall_trace(maze_tuple)
    
    fig = go.Figure(data=[wall_trace]) # 캐시된 벽으로 기본 Figure 생성

    # 2. 플레이어 위치 그리기 (이 부분만 매번 새로 계산)
    fig.add_trace(go.Scatter3d(
        x=[player_pos[2]], y=[player_pos[1]], z=[player_pos[0]],
        mode='markers',
        marker=dict(color='red', size=10, symbol='circle'),
        name='플레이어'
    ))

    # 3. 도착 지점 그리기 (이 부분도 매번 새로 계산)
    fig.add_trace(go.Scatter3d(
        x=[end_pos[2]], y=[end_pos[1]], z=[end_pos[0]],
        mode='markers',
        marker=dict(color='green', size=10, symbol='diamond'),
        name='도착'
    ))

    fig.update_layout(
        # (update_layout 부분은 기존과 동일)
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

# --- 게임 컨트롤 및 로직 ---
col1, col2 = st.columns([3, 1])

with col1:
    st.plotly_chart(create_maze_figure(), use_container_width=True)

with col2:
    st.subheader("🕹️ 컨트롤러")
    st.write(f"현재 위치: {st.session_state.player_pos}")
    st.info(st.session_state.message)

    def move_player(dz, dy, dx):
        new_pos = [
            st.session_state.player_pos[0] + dz,
            st.session_state.player_pos[1] + dy,
            st.session_state.player_pos[2] + dx,
        ]

        # 1. 미로 범위를 벗어나는지 확인
        if not (0 <= new_pos[0] < MAZE_SIZE and 0 <= new_pos[1] < MAZE_SIZE and 0 <= new_pos[2] < MAZE_SIZE):
            st.session_state.message = "미로의 끝입니다! 🚧"
            return

        # 2. 이동할 곳이 벽인지 확인
        if st.session_state.maze[tuple(new_pos)] == 1:
            st.session_state.message = "그곳은 벽입니다! 🧱"
            return
        
        # 3. 이동 성공
        st.session_state.player_pos = new_pos
        st.session_state.message = "계속 움직이세요!"

        # 4. 도착 확인
        if new_pos == st.session_state.end_pos:
            st.session_state.message = "🎉 탈출 성공! 🎉"
            st.balloons()

# --- 컨트롤러 부분 전체를 아래 코드로 교체하세요 ---
import streamlit as st
# --- 라이브러리 import (파일 상단에 있는지 확인) ---
from st_keyup import st_keyup

# ... (기존의 다른 코드들은 그대로 둡니다) ...

# --- 게임 컨트롤 및 로직 (수정된 최종 버전) ---
col1, col2 = st.columns([3, 1])

with col1:
    # 이 부분은 이전과 동일합니다.
    st.plotly_chart(create_maze_figure(), use_container_width=True, key="maze_chart")

# --- col2 부분을 아래 코드로 전체 교체 ---
with col2:
    st.subheader("🕹️ 컨트롤러")
    st.info("이제 마우스 클릭 없이 키보드로 연속 조종이 가능합니다!")
    st.write(f"현재 위치: {st.session_state.player_pos}")
    st.warning(st.session_state.message)

    # 입력창의 라벨을 session_state에 저장 (JavaScript에서 사용하기 위함)
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

    def move_player(dz, dy, dx):
        # (move_player 함수는 변경 없음)
        new_pos = [ st.session_state.player_pos[0] + dz, st.session_state.player_pos[1] + dy, st.session_state.player_pos[2] + dx, ]
        if not (0 <= new_pos[0] < MAZE_SIZE and 0 <= new_pos[1] < MAZE_SIZE and 0 <= new_pos[2] < MAZE_SIZE):
            st.session_state.message = "미로의 끝입니다! 🚧"; return
        if st.session_state.maze[tuple(new_pos)] == 1:
            st.session_state.message = "그곳은 벽입니다! 🧱"; return
        st.session_state.player_pos = new_pos
        st.session_state.message = "계속 움직이세요!"
        if new_pos == st.session_state.end_pos:
            st.session_state.message = "🎉 탈출 성공! 🎉"; st.balloons()
    
    if key:
        if key.lower() == 'e': move_player(1, 0, 0)
        elif key.lower() == 'q': move_player(-1, 0, 0)
        elif key.lower() == 'w' or key == 'ArrowUp': move_player(0, 1, 0)
        elif key.lower() == 's' or key == 'ArrowDown': move_player(0, -1, 0)
        elif key.lower() == 'd' or key == 'ArrowRight': move_player(0, 0, 1)
        elif key.lower() == 'a' or key == 'ArrowLeft': move_player(0, 0, -1)
        st.session_state.maze_controller = "" 
        st.rerun()

    st.divider()
    if st.button("새로운 미로 생성"):
        initialize_game()
        st.rerun()

    # <<<--- 맨 마지막에 이 함수를 호출해주세요! --- #
# --- 코드 최상단에 있는 autofocus_keyup 함수를 아래 코드로 교체해주세요 ---

# --- 기존 autofocus_keyup 함수를 아래 코드로 교체 ---

def autofocus_keyup():
    # 대기 시간을 200ms로 늘려 안정성 확보
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
        height=0,
        width=0,
    )