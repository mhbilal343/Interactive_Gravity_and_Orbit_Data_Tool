import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Coordinate Plane with Circles", layout="centered")

# --- Scale selection (expanded for galaxies) ---
scale_options = {
    "1,000 km/unit": 1_000,
    "10,000 km/unit (recommended)": 10_000,
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
scale_label = st.selectbox("Select Scale", list(scale_options.keys()), 
index=list(scale_options.keys()).index("10,000 km/unit (recommended)"))
SCALE = scale_options[scale_label]

# --- Top info ---
st.markdown(f"**Scale:** 1 unit = {SCALE:,} km in real life")

# --- Sidebar controls for plane ---
with st.sidebar:
    st.header("Plane Settings")
    x_min, x_max = st.slider("X-range (graph units)", -50, 50, (-25, 25), key="x_range")
    y_min, y_max = st.slider("Y-range (graph units)", -50, 50, (-25, 25), key="y_range")
    base_tick_step = st.number_input("Base Tick spacing (graph units)", 
                                     min_value=1, max_value=20, value=1, step=1)
    show_grid = st.checkbox("Show grid", value=True)

# --- Ensure circles is a dictionary ---
if "circles" not in st.session_state or not isinstance(st.session_state.circles, dict):
    st.session_state.circles = {}

# --- Add new circle ---
with st.sidebar:
    st.header("Add a New Circle")
    new_name = st.text_input("Circle Name", value=f"Circle {len(st.session_state.circles)+1}")
    new_x = st.number_input("X position (graph units)", value=0.0, key="new_x")
    new_y = st.number_input("Y position (graph units)", value=0.0, key="new_y")
    new_r = st.number_input("Radius (km)", min_value=1.0, value=5_000.0, step=1.0, key="new_r")
    new_color = st.color_picker("Color", "#0000FF", key="new_color")

    st.write(f"Real-life radius: {new_r:,} km → Graph units: {new_r / SCALE:.5f}")

    if st.button("Add Circle"):
        if new_name.strip() != "" and new_name not in st.session_state.circles:
            st.session_state.circles[new_name] = {
                "x_km": new_x * SCALE,  # store real coords in km
                "y_km": new_y * SCALE,
                "r_km": new_r,
                "color": new_color,
            }

    if st.button("Clear All Circles"):
        st.session_state.circles = {}

# --- Edit existing circles ---
with st.sidebar:
    if st.session_state.circles:
        st.header("Edit Circles")
        to_delete = []
        for name, props in list(st.session_state.circles.items()):
            st.subheader(name)
            props["x"] = st.number_input(f"{name} X (graph units)", 
                                         value=props["x_km"]/SCALE, key=f"{name}_x")
            props["y"] = st.number_input(f"{name} Y (graph units)", 
                                         value=props["y_km"]/SCALE, key=f"{name}_y")
            props["r"] = st.number_input(f"{name} Radius (km)", value=props["r_km"], 
                                         min_value=1.0, step=1.0, key=f"{name}_r")
            props["color"] = st.color_picker(f"{name} Color", value=props["color"], key=f"{name}_color")

            st.write(f"Real-life radius: {props['r_km']:,} km → Graph units: {props['r_km']/SCALE:.5f}")

            # Update km positions from graph units
            props["x_km"] = props["x"] * SCALE
            props["y_km"] = props["y"] * SCALE

            if st.button(f"Delete {name}"):
                to_delete.append(name)

        for name in to_delete:
            del st.session_state.circles[name]

# --- Create figure ---
fig = go.Figure()
theta = np.linspace(0, 2*np.pi, 200)

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
for name, props in st.session_state.circles.items():
    cx = props["x_km"] / SCALE
    cy = props["y_km"] / SCALE
    r_units = props["r_km"] / SCALE
    x_circle = cx + r_units * np.cos(theta)
    y_circle = cy + r_units * np.sin(theta)
    fig.add_trace(go.Scatter(x=x_circle, y=y_circle, mode="lines",
                             line=dict(color=props["color"]), name=name))
    fig.add_trace(go.Scatter(x=[cx], y=[cy], mode="markers+text",
                             marker=dict(size=8, color=props["color"]),
                             text=[name], textposition="top right"))

# --- Adjust ticks based on scale ---
# keep dtick reasonable so laptop doesn't fry
min_dtick, max_dtick = 0.1, 10  # limits for tick density
dtick = base_tick_step * (100_000 / SCALE**0.25)  # heuristic scaling
dtick = max(min_dtick, min(max_dtick, dtick))

fig.update_xaxes(range=[x_min, x_max], dtick=dtick, zeroline=False, showgrid=show_grid)
fig.update_yaxes(range=[y_min, y_max], dtick=dtick, zeroline=False, showgrid=show_grid)

fig.update_layout(
    width=650, height=650,
    margin=dict(l=20, r=20, t=20, b=20),
    plot_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)
