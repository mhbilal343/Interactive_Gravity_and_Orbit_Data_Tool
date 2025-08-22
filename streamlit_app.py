import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Coordinate Plane with Circles", layout="centered")

# --- Scale selection (expanded for galaxies) ---
scale_options = {
    "1,000 km/unit": 1_000,
    "10,000 km/unit": 10_000,
    "50,000 km/unit": 50_000,
    "100,000 km/unit": 100_000,
    "500,000 km/unit": 500_000,
    "1,000,000 km/unit": 1_000_000,
    "10,000,000 km/unit": 10_000_000,
    "50,000,000 km/unit": 50_000_000,
    "100,000,000 km/unit": 100_000_000,
    "500,000,000 km/unit": 500_000_000,
    "1,000,000,000 km/unit": 1_000_000_000,
    "10,000,000,000 km/unit": 10_000_000_000,
}
scale_label = st.selectbox("Select Scale", list(scale_options.keys()), index=list(scale_options.keys()).index("10,000 km/unit"))
SCALE = scale_options[scale_label]

# --- Top info ---
st.markdown(f"**Scale:** 1 unit = {SCALE:,} km in real life")

# --- Sidebar controls for plane ---
with st.sidebar:
    st.header("Plane Settings")
    x_min, x_max = st.slider("X-range", -50, 50, (-25, 25))
    y_min, y_max = st.slider("Y-range", -50, 50, (-25, 25))
    tick_step = st.number_input("Tick spacing", min_value=1, max_value=20, value=1, step=1)
    show_grid = st.checkbox("Show grid", value=True)

# --- Ensure circles is a dictionary ---
if "circles" not in st.session_state or not isinstance(st.session_state.circles, dict):
    st.session_state.circles = {}

# --- Add new circle ---
with st.sidebar:
    st.header("Add a New Circle")
    new_name = st.text_input("Circle Name", value=f"Circle {len(st.session_state.circles)+1}")
    new_x = st.number_input("X position (graph units)", value=0.0, key="new_x")  # default 0
    new_y = st.number_input("Y position (graph units)", value=0.0, key="new_y")  # default 0
    new_r = st.number_input("Radius (km)", min_value=1.0, value=5_000.0, step=100_000.0, key="new_r")  # default 5000
    new_color = st.color_picker("Color", "#0000FF", key="new_color")

    st.write(f"Real-life radius: {new_r:,} km → Graph units: {new_r / SCALE:.2f}")

    if st.button("Add Circle"):
        if new_name.strip() != "" and new_name not in st.session_state.circles:
            st.session_state.circles[new_name] = {
                "x": new_x,
                "y": new_y,
                "r": new_r,  # store in km
                "color": new_color,
            }

    if st.button("Clear All Circles"):
        st.session_state.circles = {}

# --- Edit existing circles ---
with st.sidebar:
    if st.session_state.circles:
        st.header("Edit Circles")
        to_delete = []  # keep track of circles to delete
        for name, props in list(st.session_state.circles.items()):
            st.subheader(name)
            props["x"] = st.number_input(f"{name} X (graph units)", value=props["x"], key=f"{name}_x")
            props["y"] = st.number_input(f"{name} Y (graph units)", value=props["y"], key=f"{name}_y")
            props["r"] = st.number_input(f"{name} Radius (km)", value=props["r"], min_value=1.0, step=100_000.0, key=f"{name}_r")
            props["color"] = st.color_picker(f"{name} Color", value=props["color"], key=f"{name}_color")
            
            st.write(f"Real-life radius: {props['r']:,} km → Graph units: {props['r'] / SCALE:.2f}")

            if st.button(f"Delete {name}"):
                to_delete.append(name)

        # Remove circles marked for deletion
        for name in to_delete:
            del st.session_state.circles[name]

# --- Create figure ---
fig = go.Figure()

# Invisible scatter to force ranges
fig.add_trace(go.Scatter(x=[x_min, x_max], y=[y_min, y_max],
                         mode="markers", marker_opacity=0))

# Axes with arrows
fig.add_annotation(x=x_max, y=0, ax=x_min, ay=0,
                   showarrow=True, arrowhead=3, arrowsize=1.2, arrowwidth=2, arrowcolor="black")
fig.add_annotation(x=0, y=y_max, ax=0, ay=y_min,
                   showarrow=True, arrowhead=3, arrowsize=1.2, arrowwidth=2, arrowcolor="black")

# Labels
fig.add_annotation(x=x_max, y=0, text="x", showarrow=False, xanchor="left", yanchor="bottom")
fig.add_annotation(x=0, y=y_max, text="y", showarrow=False, xanchor="left", yanchor="bottom")
fig.add_annotation(x=0, y=0, text="0", showarrow=False, xanchor="left", yanchor="bottom")

# --- Draw circles ---
theta = np.linspace(0, 2*np.pi, 200)
for name, props in st.session_state.circles.items():
    cx, cy, r_km, color = props["x"], props["y"], props["r"], props["color"]
    r_units = r_km / SCALE  # convert km to graph units
    x_circle = cx + r_units * np.cos(theta)
    y_circle = cy + r_units * np.sin(theta)
    fig.add_trace(go.Scatter(x=x_circle, y=y_circle, mode="lines",
                             line=dict(color=color), name=name))
    fig.add_trace(go.Scatter(x=[cx], y=[cy], mode="markers+text",
                             marker=dict(size=8, color=color),
                             text=[name], textposition="top right"))

# --- Layout ---
fig.update_xaxes(range=[x_min, x_max], dtick=tick_step, zeroline=False, showgrid=show_grid)
fig.update_yaxes(range=[y_min, y_max], dtick=tick_step, zeroline=False, showgrid=show_grid)

fig.update_layout(
    width=650, height=650,
    margin=dict(l=20, r=20, t=20, b=20),
    plot_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)
