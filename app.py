
"""지점 실적 대시보드 | Streamlit 디자인 리뉴얼 버전.

app.py, requirements.txt, sales.csv를 같은 폴더에 배치하세요.
실행: python -m streamlit run app.py
"""
from pathlib import Path
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st

HERE = Path(__file__).parent
COLORS = {"A": "#13B8A6", "B": "#6D7DF6"}
NAVY = "#16243B"
MUTED = "#66758C"

st.set_page_config(
    page_title="Branch Pulse | 지점 실적 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS는 화면 디자인만 바꿉니다. 데이터 분석 로직과는 관계없습니다.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], [data-testid="stApp"] {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
    }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #F1F5FB 0%, #F9FBFD 58%, #F1F5FB 100%);
    }
    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    section[data-testid="stSidebar"] {
        background: #14233B;
    }
    section[data-testid="stSidebar"] * {
        color: #EAF2FF;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        font-weight: 600;
    }
    section[data-testid="stSidebar"] [data-baseweb="select"] *,
    section[data-testid="stSidebar"] [data-baseweb="slider"] *,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: inherit;
    }
    .hero {
        background: linear-gradient(115deg, #16243B 0%, #233E63 65%, #177D81 120%);
        padding: 30px 34px;
        border-radius: 20px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 10px 28px rgba(19, 39, 69, .12);
    }
    .hero-kicker {
        color: #8FE7DD;
        font-size: 12px;
        letter-spacing: 2px;
        font-weight: 800;
        margin-bottom: 10px;
    }
    .hero-title {
        font-size: clamp(25px, 3vw, 37px);
        font-weight: 800;
        letter-spacing: -1px;
        margin: 0 0 9px 0;
    }
    .hero-sub {
        color: #D2DFEC;
        font-size: 14px;
        line-height: 1.7;
        margin: 0;
    }
    .section-title {
        color: #16243B;
        font-size: 20px;
        font-weight: 800;
        letter-spacing: -.5px;
        margin: 16px 0 10px;
    }
    .section-desc {
        color: #66758C;
        font-size: 13px;
        margin: 0 0 16px;
    }
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E5ECF5;
        border-radius: 17px;
        padding: 18px 20px;
        box-shadow: 0 4px 14px rgba(29, 52, 91, .045);
    }
    [data-testid="stMetricLabel"] {
        color: #66758C;
    }
    [data-testid="stMetricValue"] {
        color: #16243B;
        font-weight: 800;
    }
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        border-radius: 18px;
    }
    .insight {
        background: #EAF8F5;
        border-left: 4px solid #13B8A6;
        border-radius: 10px;
        padding: 15px 18px;
        color: #1F4E50;
        margin: 10px 0 22px;
        font-size: 14px;
        line-height: 1.7;
    }
    .footnote {
        color: #748196;
        font-size: 12px;
        margin-top: 18px;
    }
    @media (max-width: 680px) {
        .block-container {
            padding-top: 1rem;
        }
        .hero {
            padding: 24px 20px;
            border-radius: 16px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    # 절대경로 대신 app.py 옆의 sales.csv를 찾습니다.
    return pd.read_csv(HERE / "sales.csv")


def korean_font():
    names = {f.name for f in fm.fontManager.ttflist}
    return next(
        (
            name for name in [
                "Pretendard",
                "Malgun Gothic",
                "AppleGothic",
                "NanumGothic"
            ]
            if name in names
        ),
        None,
    )


# ── 상단 소개 ──

st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">
            BRANCH PULSE · PERFORMANCE OVERVIEW
        </div>
        <div class="hero-title">
            지점 실적 인사이트 대시보드
        </div>
        <p class="hero-sub">
            지점별 매출과 영업이익을 한눈에 비교하고,
            기간에 따른 변화와 수익성을 탐색해 보세요.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


try:
    data = load_data()
except FileNotFoundError:
    st.error(
        "sales.csv 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더에 넣어 주세요."
    )
    st.stop()

required = {"branch", "month", "sales", "profit"}

if not required.issubset(data.columns):
    st.error(
        f"CSV에 필요한 열이 없습니다: "
        f"{', '.join(sorted(required - set(data.columns)))}"
    )
    st.stop()


# ── 왼쪽 필터 ──

st.sidebar.markdown("## ◈ BRANCH PULSE")
st.sidebar.caption("PERFORMANCE CONTROL PANEL")
st.sidebar.divider()

st.sidebar.markdown("### 조회 조건")

branches = st.sidebar.multiselect(
    "지점 선택",
    ["A", "B"],
    default=["A", "B"]
)

months = st.sidebar.slider(
    "조회 월",
    1,
    12,
    (1, 12)
)

metric_label = st.sidebar.selectbox(
    "분석 지표",
    ["매출", "영업이익"]
)

metric = {
    "매출": "sales",
    "영업이익": "profit"
}[metric_label]

st.sidebar.divider()
st.sidebar.caption("DATA  |  2026년 1~12월")
st.sidebar.caption("SOURCE  |  수업용 가상 데이터")
st.sidebar.caption("UNIT  |  백만원")


# ── 데이터 필터링 ──

view = data.loc[
    data["branch"].isin(branches)
    & data["month"].between(months[0], months[1])
].copy()

if view.empty:
    st.warning(
        "현재 조건에 맞는 데이터가 없습니다. "
        "왼쪽에서 지점을 하나 이상 선택해 주세요."
    )
    st.stop()


# ── 핵심 지표 계산 ──

selected_total = view[metric].sum()
sales_total = view["sales"].sum()
profit_total = view["profit"].sum()

margin = (
    profit_total / sales_total * 100
    if sales_total != 0
    else 0.0
)

branch_totals = view.groupby(
    "branch",
    as_index=False
)[metric].sum()

best_branch = branch_totals.loc[
    branch_totals[metric].idxmax(),
    "branch"
]


# ── 핵심 지표 화면 ──

st.markdown(
    '<div class="section-title">핵심 지표</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<p class="section-desc">'
    f'2026년 {months[0]}~{months[1]}월 · '
    f'{", ".join(branches)}지점 · '
    f'{metric_label} 기준'
    f'</p>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    f"기간 {metric_label} 합계",
    f"{selected_total:,.0f} 백만원"
)

c2.metric(
    "기간 영업이익률",
    f"{margin:.1f}%"
)

c3.metric(
    "분석 데이터",
    f"{len(view):,}건"
)

c4.metric(
    f"{metric_label} 1위 지점",
    f"{best_branch} 지점"
)


# ── 자동 요약 문구 ──

st.markdown(
    f'<div class="insight">'
    f'<b>데이터 한눈에 보기</b> · '
    f'선택 기간의 {metric_label} 합계는 '
    f'<b>{selected_total:,.0f}백만원</b>이며, '
    f'{metric_label} 기준으로 '
    f'<b>{best_branch}지점</b>이 가장 높습니다. '
    f'기간 전체 영업이익률은 '
    f'<b>{margin:.1f}%</b>입니다.'
    f'</div>',
    unsafe_allow_html=True
)


# ── 차트 공통 디자인 ──

plot_bg = "#FFFFFF"
grid_color = "#EDF1F6"


# ── 차트 1: 월별 추이 ──

trend = px.line(
    view.sort_values(["branch", "month"]),
    x="month",
    y=metric,
    color="branch",
    markers=True,
    color_discrete_map=COLORS,
    labels={
        "month": "월",
        metric: f"{metric_label} (백만원)",
        "branch": "지점"
    },
)

trend.update_traces(
    line_width=3,
    marker_size=8
)

trend.update_layout(
    height=360,
    paper_bgcolor=plot_bg,
    plot_bgcolor=plot_bg,
    margin=dict(l=15, r=15, t=20, b=20),
    font=dict(
        family="Arial, sans-serif",
        color=NAVY
    ),
    hovermode="x unified",
    legend=dict(
        orientation="h",
        y=1.12,
        x=0
    ),
)

trend.update_xaxes(
    dtick=1,
    showgrid=False,
    zeroline=False
)

trend.update_yaxes(
    rangemode="tozero",
    gridcolor=grid_color,
    zeroline=False
)

st.markdown(
    '<div class="section-title">월별 실적 흐름</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="section-desc">'
    '선 위에 마우스를 올리면 월별 값을 확인할 수 있습니다.'
    '</p>',
    unsafe_allow_html=True
)

with st.container(border=True):
    st.plotly_chart(
        trend,
        width="stretch"
    )


# ── 차트 2: 지점별 합계 ──

totals = view.groupby(
    "branch",
    as_index=False
)[metric].sum()

kfont = korean_font()

with plt.rc_context({
    "font.family": kfont or "DejaVu Sans",
    "axes.unicode_minus": False
}):
    static_fig, ax = plt.subplots(
        figsize=(6, 4)
    )

    static_fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    bars = ax.bar(
        totals["branch"],
        totals[metric],
        width=0.55,
        color=[
            COLORS[b]
            for b in totals["branch"]
        ],
    )

    ax.bar_label(
        bars,
        fmt="%.0f",
        padding=5,
        fontsize=11,
        fontweight="bold",
        color=NAVY
    )

    if kfont:
        ax.set(
            xlabel="지점",
            ylabel=f"{metric_label} (백만원)"
        )
    else:
        ax.set(
            xlabel="Branch",
            ylabel=f"{metric} (million KRW)"
        )

    ax.set_ylim(
        0,
        max(totals[metric].max() * 1.25, 1)
    )

    ax.grid(
        axis="y",
        alpha=0.18
    )

    ax.set_axisbelow(True)

    ax.spines[
        ["top", "right", "left"]
    ].set_visible(False)

    static_fig.tight_layout()


# ── 차트 3: 지점별 영업이익률 ──

period = view.groupby(
    "branch",
    as_index=False
)[["sales", "profit"]].sum()

period["margin"] = (
    period["profit"]
    / period["sales"].replace(
        0,
        float("nan")
    )
    * 100
).fillna(0)

margin_fig = px.bar(
    period,
    x="branch",
    y="margin",
    color="branch",
    color_discrete_map=COLORS,
    text=period["margin"].map(
        lambda value: f"{value:.1f}%"
    ),
    labels={
        "branch": "지점",
        "margin": "영업이익률 (%)"
    },
)

margin_fig.update_traces(
    textposition="outside",
    marker_line_width=0
)

margin_fig.update_layout(
    height=330,
    paper_bgcolor=plot_bg,
    plot_bgcolor=plot_bg,
    margin=dict(
        l=15,
        r=15,
        t=25,
        b=20
    ),
    showlegend=False,
    font=dict(
        family="Arial, sans-serif",
        color=NAVY
    ),
)

margin_fig.update_xaxes(
    showgrid=False
)

margin_fig.update_yaxes(
    rangemode="tozero",
    gridcolor=grid_color,
    zeroline=False
)


# ── 두 차트를 나란히 배치 ──

st.markdown(
    '<div class="section-title">지점별 비교</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="section-desc">'
    '기간 합계와 영업이익률을 함께 보면 '
    '규모와 수익성을 비교할 수 있습니다.'
    '</p>',
    unsafe_allow_html=True
)

left, right = st.columns(2)

with left:
    with st.container(border=True):
        st.markdown(
            "**지점별 기간 합계**"
        )
        st.pyplot(
            static_fig,
            width="stretch"
        )

with right:
    with st.container(border=True):
        st.markdown(
            "**지점별 기간 영업이익률**"
        )
        st.plotly_chart(
            margin_fig,
            width="stretch"
        )

plt.close(static_fig)

if not kfont:
    st.caption(
        "참고: 서버에 한글 글꼴이 없어 "
        "왼쪽 Matplotlib 차트의 축 이름은 "
        "영어로 표시됩니다."
    )


# ── 데이터 표와 CSV 다운로드 ──

st.markdown(
    '<div class="section-title">데이터 상세 보기</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="section-desc">'
    '현재 조회 조건에 포함된 원본 행만 표시합니다.'
    '</p>',
    unsafe_allow_html=True
)

with st.container(border=True):

    st.dataframe(
        view.sort_values([
            "branch",
            "month"
        ]),
        hide_index=True,
        width="stretch"
    )

    st.download_button(
        "⬇ 현재 선택 데이터 CSV 다운로드",
        data=view.to_csv(
            index=False
        ).encode("utf-8-sig"),
        file_name="selected_sales.csv",
        mime="text/csv"
    )


# ── 하단 안내 ──

st.markdown(
    '<div class="footnote">'
    '출처: 수업용 가상 데이터(sales.csv) · '
    '2026년 1~12월 · 단위: 백만원 · '
    '이 자료만으로 실적 차이의 원인을 '
    '단정할 수 없습니다.'
    '</div>',
    unsafe_allow_html=True
)
