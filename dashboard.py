import tempfile
from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from streamlit_mic_recorder import mic_recorder
except ImportError:
    mic_recorder = None

from app.config import (
    DATABASE_URL,
    OLLAMA_MODEL,
    OPENAI_MODEL,
    SPEECHMATICS_API_KEY,
    TEXT_TO_SQL_PROVIDER,
)
from app.database.query_engine import get_schema, run_nl_query
from app.speech.speech_to_text import transcribe_audio_file


st.set_page_config(page_title="Voice2Query", layout="wide")

st.markdown("""
<style>
:root {
    --bg: #030805;
    --panel: rgba(8, 18, 12, 0.88);
    --panel-strong: rgba(10, 24, 14, 0.96);
    --line-green: rgba(74, 222, 128, 0.26);
    --line-gold: rgba(250, 204, 21, 0.28);
    --green: #4ade80;
    --green-2: #22c55e;
    --gold: #facc15;
    --gold-2: #f59e0b;
    --text: #f8fafc;
    --muted: #a7b2a4;
}

.stApp {
    background:
        radial-gradient(circle at 18% 8%, rgba(74, 222, 128, 0.16), transparent 32%),
        radial-gradient(circle at 82% 2%, rgba(250, 204, 21, 0.14), transparent 28%),
        radial-gradient(circle at 50% 100%, rgba(34, 197, 94, 0.08), transparent 38%),
        linear-gradient(135deg, #020403, #061009 42%, #030805);
}

[data-testid="stHeader"],
#MainMenu,
footer {
    visibility: hidden;
    height: 0;
}

section[data-testid="stSidebar"] {
    display: none;
}

.block-container {
    max-width: 1320px;
    padding-top: 0.55rem;
    padding-bottom: 3rem;
}

.neon-hero {
    border: 1px solid var(--line-green);
    border-radius: 18px;
    background:
        linear-gradient(135deg, rgba(74, 222, 128, 0.10), rgba(250, 204, 21, 0.08)),
        rgba(3, 8, 5, 0.82);
    padding: 1rem 1.25rem;
    box-shadow:
        0 0 42px rgba(74, 222, 128, 0.14),
        inset 0 1px 0 rgba(255, 255, 255, 0.06);
    margin-bottom: 0.85rem;
}

.hero-kicker {
    color: var(--gold);
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.hero-title {
    color: var(--text);
    font-size: clamp(2.25rem, 4vw, 3.9rem);
    font-weight: 900;
    line-height: 0.98;
    margin: 0.2rem 0;
    text-shadow: 0 0 28px rgba(74, 222, 128, 0.28);
}

.hero-subtitle {
    color: var(--muted);
    font-size: 0.98rem;
    max-width: 900px;
}

.signal-strip {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.65rem;
    margin: 0.75rem 0 0.95rem;
}

.signal-card {
    border: 1px solid var(--line-green);
    border-radius: 14px;
    background: rgba(8, 18, 12, 0.86);
    padding: 0.68rem 0.82rem;
    box-shadow: 0 0 20px rgba(74, 222, 128, 0.08);
}

.signal-label {
    color: var(--muted);
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.signal-value {
    color: var(--green);
    font-size: 0.92rem;
    font-weight: 800;
    margin-top: 0.25rem;
    overflow-wrap: anywhere;
}

.input-panel {
    border: 1px solid var(--line-green);
    border-radius: 16px;
    background:
        linear-gradient(180deg, rgba(74, 222, 128, 0.07), rgba(8, 18, 12, 0.88)),
        var(--panel);
    padding: 0.62rem 0.78rem;
    min-height: 128px;
    box-shadow: 0 0 32px rgba(74, 222, 128, 0.09);
}

.input-panel.gold {
    border-color: var(--line-gold);
    background:
        linear-gradient(180deg, rgba(250, 204, 21, 0.08), rgba(8, 18, 12, 0.88)),
        var(--panel);
    box-shadow: 0 0 32px rgba(250, 204, 21, 0.09);
}

.panel-icon {
    font-size: 1.15rem;
    margin-bottom: 0.1rem;
}

.panel-title {
    color: var(--text);
    font-size: 1rem;
    font-weight: 900;
    margin-bottom: 0.15rem;
}

.panel-copy {
    color: var(--muted);
    font-size: 0.84rem;
    margin-bottom: 0.45rem;
}

.voice-note {
    border: 1px solid rgba(74, 222, 128, 0.22);
    border-radius: 12px;
    background: rgba(74, 222, 128, 0.08);
    color: #bbf7d0;
    padding: 0.58rem 0.7rem;
    margin: 0.45rem 0;
}

.query-button-wrap {
    max-width: 720px;
    margin: 0.95rem auto 1.2rem;
}

button[kind="primary"] {
    min-height: 3rem;
    border-radius: 16px !important;
    font-weight: 900 !important;
    letter-spacing: 0.02em;
    background: linear-gradient(90deg, #16a34a, #facc15) !important;
    color: #041007 !important;
    border: 0 !important;
    box-shadow: 0 0 36px rgba(250, 204, 21, 0.26) !important;
}

div[data-testid="stButton"] button:not([kind="primary"]) {
    min-height: 3.15rem;
    border-radius: 14px;
    font-weight: 800;
    border-color: rgba(74, 222, 128, 0.34);
}

.answer-shell {
    border: 1px solid var(--line-green);
    border-radius: 18px;
    background: rgba(8, 18, 12, 0.88);
    padding: 1rem;
    box-shadow: 0 0 44px rgba(74, 222, 128, 0.10);
}

.answer-title {
    color: var(--text);
    font-size: 1.8rem;
    font-weight: 900;
}

.answer-subtitle {
    color: var(--muted);
    margin-bottom: 1rem;
}

.section-title {
    color: var(--gold);
    font-size: 1.22rem;
    font-weight: 900;
    margin: 1.35rem 0 0.65rem;
}

.question-box {
    border: 1px solid rgba(250, 204, 21, 0.28);
    border-left: 5px solid var(--gold);
    border-radius: 14px;
    background: rgba(250, 204, 21, 0.08);
    color: var(--text);
    padding: 1rem 1.1rem;
}

.sql-box {
    border: 1px solid rgba(74, 222, 128, 0.28);
    border-left: 5px solid var(--green);
    border-radius: 14px;
    background: #020604;
    color: #d9f99d;
    padding: 1rem;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.95rem;
    white-space: pre-wrap;
    overflow-x: auto;
}

.metric-card {
    border: 1px solid rgba(74, 222, 128, 0.25);
    border-radius: 16px;
    background:
        linear-gradient(180deg, rgba(74, 222, 128, 0.08), rgba(250, 204, 21, 0.03)),
        rgba(8, 18, 12, 0.94);
    padding: 1rem;
    min-height: 112px;
    box-shadow: 0 0 28px rgba(74, 222, 128, 0.10);
}

.metric-label {
    color: var(--muted);
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.metric-value {
    color: var(--gold);
    font-size: 2rem;
    font-weight: 900;
    margin-top: 0.25rem;
}

.insight-box {
    border: 1px solid rgba(250, 204, 21, 0.28);
    border-radius: 16px;
    background: rgba(250, 204, 21, 0.08);
    padding: 1rem 1.1rem;
    color: var(--text);
}

.single-list {
    border: 1px solid rgba(74, 222, 128, 0.24);
    border-radius: 14px;
    overflow: hidden;
    background: #020604;
}

.single-list-row {
    border-bottom: 1px solid rgba(74, 222, 128, 0.16);
    color: var(--text);
    padding: 0.78rem 1rem;
}

.single-list-row:last-child {
    border-bottom: 0;
}

div[data-testid="stDataFrame"] {
    border: 1px solid rgba(74, 222, 128, 0.24);
    border-radius: 14px;
    overflow: hidden;
}

.tool-footer {
    border: 1px solid var(--line-gold);
    border-radius: 20px;
    background: rgba(8, 18, 12, 0.86);
    padding: 1.1rem;
    margin-top: 1.4rem;
}

.tool-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.75rem;
}

.tool-pill {
    border: 1px solid rgba(250, 204, 21, 0.22);
    border-radius: 14px;
    background: rgba(250, 204, 21, 0.06);
    color: var(--text);
    padding: 0.85rem;
    font-weight: 800;
}

@media (max-width: 900px) {
    .signal-strip,
    .tool-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}
</style>
""", unsafe_allow_html=True)


def visible_database_url() -> str:
    return DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL


def metric_card(label: str, value: str | int | float) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{escape(str(label))}</div>
            <div class="metric-value">{escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_metric_value(value) -> str:
    if pd.isna(value):
        return "-"
    if isinstance(value, float):
        return f"{value:,.2f}"
    return str(value)


def render_result_list(df: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">📋 Result List</div>', unsafe_allow_html=True)
    if df.empty:
        st.info("The query ran successfully but returned no rows.")
        return

    if len(df.columns) == 1:
        column = df.columns[0]
        rows = df[column].head(25).tolist()
        list_html = "".join(
            f'<div class="single-list-row">{index}. {escape(str(value))}</div>'
            for index, value in enumerate(rows, start=1)
        )
        st.markdown(f'<div class="single-list">{list_html}</div>', unsafe_allow_html=True)
        if len(df) > 25:
            st.caption(f"Showing first 25 of {len(df)} rows.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


def render_list_visual(df: pd.DataFrame) -> bool:
    if df.empty or len(df.columns) != 1:
        return False

    column = df.columns[0]
    if pd.api.types.is_numeric_dtype(df[column]):
        return False

    values = df[column].dropna().astype(str).head(12).tolist()
    if not values:
        return False

    rows = "".join(
        f"""
        <div class="single-list-row">
            <span style="color:#facc15;font-weight:900;margin-right:0.75rem;">#{index}</span>
            {escape(value)}
        </div>
        """
        for index, value in enumerate(values, start=1)
    )
    st.markdown(
        f"""
        <div class="single-list">
            {rows}
        </div>
        """,
        unsafe_allow_html=True,
    )
    return True


def render_insights(df: pd.DataFrame) -> None:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = [column for column in df.columns if column not in numeric_cols]

    st.markdown('<div class="section-title">⚡ Quick Insights</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Rows", len(df))
    with c2:
        metric_card("Columns", len(df.columns))
    with c3:
        metric_card("Numeric fields", len(numeric_cols))
    with c4:
        if categorical_cols:
            metric_card("Unique values", df[categorical_cols[0]].nunique())
        elif numeric_cols:
            metric_card("Average", format_metric_value(df[numeric_cols[0]].mean()))
        else:
            metric_card("Fields", len(df.columns))


def insight_items(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return ["The query completed successfully, but no rows matched the question."]

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = [column for column in df.columns if column not in numeric_cols]
    items = [f"The result contains {len(df):,} rows across {len(df.columns):,} columns."]

    if categorical_cols:
        first_cat = categorical_cols[0]
        top_value = df[first_cat].mode(dropna=True)
        if not top_value.empty:
            top_count = int((df[first_cat] == top_value.iloc[0]).sum())
            items.append(
                f"The most common {first_cat} is {top_value.iloc[0]} with {top_count:,} matching rows."
            )
        items.append(f"{first_cat} has {df[first_cat].nunique():,} unique values.")

    if numeric_cols:
        first_num = numeric_cols[0]
        items.append(
            f"{first_num} ranges from {format_metric_value(df[first_num].min())} "
            f"to {format_metric_value(df[first_num].max())}."
        )
        items.append(f"The average {first_num} is {format_metric_value(df[first_num].mean())}.")

    return items[:4]


def render_narrative_insights(df: pd.DataFrame) -> None:
    items = "".join(f"<li>{escape(item)}</li>" for item in insight_items(df))
    st.markdown(
        f"""
        <div class="insight-box">
            <strong>🧠 Insight Summary</strong>
            <ul>{items}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_figure(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc"),
        title_font=dict(color="#facc15", size=18),
        margin=dict(t=60, b=20, l=20, r=20),
    )
    fig.update_xaxes(gridcolor="rgba(74, 222, 128, 0.12)")
    fig.update_yaxes(gridcolor="rgba(74, 222, 128, 0.12)")
    return fig


def render_plots(df: pd.DataFrame) -> None:
    if df.empty:
        return

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    all_categorical_cols = [column for column in df.columns if column not in numeric_cols]
    categorical_cols = [
        column
        for column in all_categorical_cols
        if not any(token in column.lower() for token in ["name", "id", "email", "phone"])
        and 1 < df[column].nunique(dropna=True) <= min(20, max(2, len(df) // 2))
    ]

    st.markdown('<div class="section-title">📊 Visual Insights</div>', unsafe_allow_html=True)
    chart_template = "plotly_dark"
    colors = ["#4ade80", "#facc15", "#22c55e", "#f59e0b", "#bbf7d0"]

    if render_list_visual(df):
        st.caption(
            "This query returned a list, so the best visual is a ranked preview. "
            "For charts, ask for grouped counts or averages."
        )
        return

    if categorical_cols and numeric_cols:
        grouped = (
            df.groupby(categorical_cols[0], dropna=False)[numeric_cols[0]]
            .sum()
            .reset_index()
            .sort_values(numeric_cols[0], ascending=False)
            .head(15)
        )
        left, right = st.columns(2)
        with left:
            fig = px.bar(
                grouped,
                x=categorical_cols[0],
                y=numeric_cols[0],
                title=f"{numeric_cols[0]} by {categorical_cols[0]}",
                color_discrete_sequence=colors,
                template=chart_template,
            )
            st.plotly_chart(style_figure(fig), use_container_width=True)
        with right:
            fig = px.pie(
                grouped,
                names=categorical_cols[0],
                values=numeric_cols[0],
                title=f"Share of {numeric_cols[0]}",
                color_discrete_sequence=colors,
                template=chart_template,
            )
            st.plotly_chart(style_figure(fig), use_container_width=True)
        return

    if categorical_cols:
        counts = df[categorical_cols[0]].value_counts().head(15).reset_index()
        counts.columns = [categorical_cols[0], "count"]
        fig = px.bar(
            counts,
            x="count",
            y=categorical_cols[0],
            title=f"Count by {categorical_cols[0]}",
            orientation="h",
            color_discrete_sequence=colors,
            template=chart_template,
        )
        fig.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(style_figure(fig), use_container_width=True)
        return

    if len(all_categorical_cols) == 1 and not numeric_cols:
        st.info(
            "This result is mostly a list, so a chart would not add much. "
            "Try asking for a grouped answer like students by city or department."
        )
        return

    if numeric_cols:
        left, right = st.columns(2)
        with left:
            fig = px.histogram(
                df,
                x=numeric_cols[0],
                title=f"Distribution of {numeric_cols[0]}",
                color_discrete_sequence=colors,
                template=chart_template,
            )
            st.plotly_chart(style_figure(fig), use_container_width=True)
        with right:
            fig = px.line(
                df.reset_index(),
                x="index",
                y=numeric_cols[0],
                title=f"{numeric_cols[0]} across result order",
                color_discrete_sequence=colors,
                template=chart_template,
            )
            st.plotly_chart(style_figure(fig), use_container_width=True)


def render_tool_footer() -> None:
    model_name = OPENAI_MODEL if TEXT_TO_SQL_PROVIDER == "openai" else OLLAMA_MODEL
    tools = [
        ("🐘", "PostgreSQL", visible_database_url()),
        ("🎙️", "Speechmatics", "Configured" if SPEECHMATICS_API_KEY else "Waiting for key"),
        ("🧠", "Text-to-SQL", TEXT_TO_SQL_PROVIDER),
        ("🦙", "Model", model_name),
        ("🎛️", "Streamlit", "Dashboard"),
        ("🔗", "SQLAlchemy", "Database engine"),
        ("📊", "Plotly", "Charts"),
        ("🐍", "Python", "Backend"),
    ]
    pills = "".join(
        f"""
        <div class="tool-pill">
            {icon} {escape(name)}<br>
            <span style="color:#a7b2a4;font-size:0.85rem;">{escape(value)}</span>
        </div>
        """
        for icon, name, value in tools
    )
    st.markdown(
        f"""
        <div class="tool-footer">
            <div class="section-title" style="margin-top:0;">🛠️ Tools Used</div>
            <div class="tool-grid">{pills}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_query_examples() -> None:
    examples = [
        "students in each department",
        "average attendance by department",
        "students from Naples",
        "top 10 students by attendance",
        "average age by city",
        "number of students in each city",
    ]
    chips = "".join(
        f'<div class="tool-pill">💡 {escape(example)}</div>'
        for example in examples
    )
    st.markdown(
        f"""
        <div class="tool-footer">
            <div class="section-title" style="margin-top:0;">✨ Query Ideas</div>
            <div class="tool-grid">{chips}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


model_name = OPENAI_MODEL if TEXT_TO_SQL_PROVIDER == "openai" else OLLAMA_MODEL
speech_status = "Configured" if SPEECHMATICS_API_KEY else "Waiting for key"

st.markdown(
    """
    <div class="neon-hero">
        <div class="hero-kicker">⚡ AI powered speech-to-SQL dashboard</div>
        <div class="hero-title">🎤 Voice2Query</div>
        <div class="hero-subtitle">
            Speak or type a database question, generate PostgreSQL instantly, and explore the answer with neon insights.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="signal-strip">
        <div class="signal-card">
            <div class="signal-label">🐘 Database</div>
            <div class="signal-value">{escape(visible_database_url())}</div>
        </div>
        <div class="signal-card">
            <div class="signal-label">🧠 SQL Engine</div>
            <div class="signal-value">{escape(TEXT_TO_SQL_PROVIDER)}</div>
        </div>
        <div class="signal-card">
            <div class="signal-label">🦙 Model</div>
            <div class="signal-value">{escape(model_name)}</div>
        </div>
        <div class="signal-card">
            <div class="signal-label">🎙️ Speechmatics</div>
            <div class="signal-value">{escape(speech_status)}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns(2, gap="large")

with left:
    st.markdown(
        """
        <div class="input-panel">
            <div class="panel-icon">🎙️</div>
            <div class="panel-title">Voice Query</div>
            <div class="panel-copy">Record your question and transcribe it through Speechmatics.</div>
        """,
        unsafe_allow_html=True,
    )

    if not SPEECHMATICS_API_KEY:
        st.markdown(
            '<div class="voice-note">Add SPEECHMATICS_API_KEY to .env to enable transcription.</div>',
            unsafe_allow_html=True,
        )

    recorded_audio = None
    if mic_recorder is None:
        st.error("Install microphone support with: `pip install streamlit-mic-recorder`")
    else:
        recorded_audio = mic_recorder(
            start_prompt="🎙️ Start recording",
            stop_prompt="⏹️ Stop recording",
            just_once=False,
            use_container_width=True,
            key="voice_query_recorder",
        )

    if recorded_audio and recorded_audio.get("bytes"):
        st.audio(recorded_audio["bytes"])
        if st.button(
            "✨ Transcribe voice",
            use_container_width=True,
            disabled=not SPEECHMATICS_API_KEY,
        ):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(recorded_audio["bytes"])
                temp_path = temp_file.name

            with st.spinner("Transcribing with Speechmatics..."):
                transcript, error = transcribe_audio_file(temp_path)

            Path(temp_path).unlink(missing_ok=True)
            if error:
                st.error(error)
            else:
                st.session_state["audio_transcript"] = transcript
                st.success("Voice converted to text.")
    else:
        st.caption("No recording captured yet.")

    audio_query = st.text_area(
        "Voice transcript",
        value=st.session_state.get("audio_transcript", ""),
        height=54,
        placeholder="Transcript appears here.",
    )

    with st.expander("Upload audio file instead"):
        audio_file = st.file_uploader(
            "Upload an audio file",
            type=["wav", "mp3", "m4a", "flac", "ogg", "webm"],
        )
        if st.button(
            "Transcribe uploaded file",
            use_container_width=True,
            disabled=not SPEECHMATICS_API_KEY,
        ):
            if not audio_file:
                st.warning("Upload an audio file first.")
            else:
                suffix = Path(audio_file.name).suffix or ".wav"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                    temp_file.write(audio_file.getbuffer())
                    temp_path = temp_file.name
                with st.spinner("Transcribing with Speechmatics..."):
                    transcript, error = transcribe_audio_file(temp_path)
                Path(temp_path).unlink(missing_ok=True)
                if error:
                    st.error(error)
                else:
                    st.session_state["audio_transcript"] = transcript
                    st.success("Audio converted to text.")

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown(
        """
        <div class="input-panel gold">
            <div class="panel-icon">⌨️</div>
            <div class="panel-title">Text Query</div>
            <div class="panel-copy">Type naturally. The model will turn your request into PostgreSQL.</div>
        """,
        unsafe_allow_html=True,
    )
    text_query = st.text_area(
        "Natural language query",
        placeholder="Example: students in each department",
        height=76,
    )
    st.markdown("</div>", unsafe_allow_html=True)

query = text_query.strip() or audio_query.strip()

st.markdown('<div class="query-button-wrap">', unsafe_allow_html=True)
run_clicked = st.button("🚀 Generate Query & Reveal Insights", type="primary", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

if run_clicked:
    if not query:
        st.warning("Speak or type a question first.")
    else:
        with st.spinner("Generating SQL and querying Postgres..."):
            sql, df, error = run_nl_query(query)
        st.session_state["last_query"] = query
        st.session_state["last_sql"] = sql
        st.session_state["last_df"] = df
        st.session_state["last_error"] = error

if st.session_state.get("last_query"):
    st.markdown(
        """
        <div class="answer-shell">
            <div class="answer-title">🌟 Insight Console</div>
            <div class="answer-subtitle">Query, SQL, data list, and visual analytics generated from your database.</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-title">💬 Query</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="question-box">{escape(st.session_state["last_query"])}</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.get("last_sql"):
        st.markdown('<div class="section-title">🧾 Generated SQL</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sql-box">{escape(st.session_state["last_sql"])}</div>',
            unsafe_allow_html=True,
        )

    if st.session_state.get("last_error"):
        st.error(st.session_state["last_error"])
    elif st.session_state.get("last_df") is not None:
        result_df = st.session_state["last_df"]
        render_insights(result_df)
        render_narrative_insights(result_df)
        render_result_list(result_df)
        render_plots(result_df)
        st.download_button(
            "⬇️ Download result CSV",
            data=result_df.to_csv(index=False).encode("utf-8"),
            file_name="voice2query_results.csv",
            mime="text/csv",
        )
    st.markdown("</div>", unsafe_allow_html=True)

schema, schema_error = get_schema()
render_query_examples()
render_tool_footer()

with st.expander("🗄️ Database schema"):
    if schema_error:
        st.error(schema_error)
    else:
        st.code(schema, language="text")
