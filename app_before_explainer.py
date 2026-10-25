

import streamlit as st
import pandas as pd
from itertools import combinations

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="GridRescue | Blackout Restoration",
    page_icon="⚡",
    layout="wide"
)

# ---------------- DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #08111F, #101D33);
    color: #EAF4FF;
}
[data-testid="stSidebar"] {
    background-color: #111C30;
}
h1, h2, h3 {
    color: #55D6FF !important;
}
div[data-testid="stMetric"] {
    background: rgba(30, 55, 85, 0.65);
    border: 1px solid rgba(85, 214, 255, 0.25);
    padding: 16px;
    border-radius: 12px;
}
.stCaption {
    color: #B8C9DD;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FACILITY DATA ----------------

FACILITIES = [
    {"name": "Hospital", "demand": 40, "priority": 5},
    {"name": "Water Pump", "demand": 25, "priority": 4},
    {"name": "Mobile Tower", "demand": 15, "priority": 4},
    {"name": "Emergency Shelter", "demand": 30, "priority": 3},
    {"name": "Streetlights", "demand": 20, "priority": 2},
    {"name": "Public Charging", "demand": 30, "priority": 1},
]

# ---------------- RESTORATION ALGORITHM ----------------

def make_plan(facilities, available_power):
    best_group = []
    best_score = -1
    best_used = 0

    for size in range(len(facilities) + 1):
        for group in combinations(facilities, size):
            used = sum(f["demand"] for f in group)

            if used > available_power:
                continue

            score = sum(
                f["priority"] * f["demand"]
                for f in group
            )

            if (
                score > best_score
                or (
                    score == best_score
                    and used > best_used
                )
            ):
                best_group = list(group)
                best_score = score
                best_used = used

    return best_group


def create_plan_table(facilities, selected, available_power):
    selected_names = {f["name"] for f in selected}

    rows = []

    for facility in facilities:
        powered = facility["name"] in selected_names

        rows.append({
            "Facility": facility["name"],
            "Demand (kW)": facility["demand"],
            "Priority": facility["priority"],
            "Supplied (kW)": (
                facility["demand"] if powered else 0
            ),
            "Status": "POWERED" if powered else "NOT RESTORED"
        })

    return pd.DataFrame(rows)


# ---------------- HEADER ----------------

st.title("⚡ GRIDRESCUE")
st.caption(
    "SMART MICRO-GRID | BLACKOUT RESTORATION "
    "AND EMERGENCY POWER ALLOCATION"
)

st.markdown(
    "An intelligent decision-support dashboard that allocates "
    "limited electricity to essential services during a blackout."
)

# ---------------- CONTROLS ----------------

st.sidebar.title("⚙️ Microgrid Controls")
st.sidebar.caption("Adjust power availability and simulate failures.")

solar_power = st.sidebar.slider(
    "Solar generation (kW)",
    min_value=0,
    max_value=100,
    value=60,
    step=5
)

battery_power = st.sidebar.slider(
    "Battery backup (kW)",
    min_value=0,
    max_value=100,
    value=40,
    step=5
)

failure_event = st.sidebar.selectbox(
    "Simulate blackout event",
    [
        "No failure",
        "Solar drop",
        "Solar failure",
        "Battery failure",
        "Solar and battery failure"
    ]
)

# ---------------- FAILURE SIMULATION ----------------

normal_power = solar_power + battery_power

actual_solar = solar_power
actual_battery = battery_power

if failure_event == "Solar drop":
    actual_solar = max(0, solar_power - 30)

elif failure_event == "Solar failure":
    actual_solar = 0

elif failure_event == "Battery failure":
    actual_battery = 0

elif failure_event == "Solar and battery failure":
    actual_solar = 0
    actual_battery = 0

available = actual_solar + actual_battery

# ---------------- MICROGRID OVERVIEW ----------------

st.header("Microgrid Overview")

total_demand = sum(
    facility["demand"] for facility in FACILITIES
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Solar available", f"{actual_solar} kW")
c2.metric("Battery available", f"{actual_battery} kW")
c3.metric("Power available", f"{available} kW")
c4.metric("Total demand", f"{total_demand} kW")



# ---------------- BLACKOUT WAR ROOM ----------------

st.header("⚔️ Blackout War Room")
st.caption(
    "Compare restoration strategies using the same available power."
)

priority_plan = make_plan(FACILITIES, available)

coverage_plan = []
best_count = -1
best_score = -1
best_used = 0

for size in range(len(FACILITIES) + 1):
    for group in combinations(FACILITIES, size):
        used = sum(f["demand"] for f in group)

        if used > available:
            continue

        score = sum(f["priority"] * f["demand"] for f in group)

        if (
            size > best_count
            or (size == best_count and score > best_score)
            or (
                size == best_count
                and score == best_score
                and used > best_used
            )
        ):
            coverage_plan = list(group)
            best_count = size
            best_score = score
            best_used = used

war1, war2 = st.columns(2)

with war1:
    st.subheader("🎯 Priority Optimizer")
    st.write("Focus: importance of the services.")
    st.metric("Facilities restored", len(priority_plan))
    st.metric(
        "Power allocated",
        f"{sum(f['demand'] for f in priority_plan)} kW"
    )
    st.write(
        ", ".join(f["name"] for f in priority_plan)
        or "No facilities restored"
    )

with war2:
    st.subheader("🌐 Maximum Coverage")
    st.write("Focus: restoring the greatest number of facilities.")
    st.metric("Facilities restored", len(coverage_plan))
    st.metric(
        "Power allocated",
        f"{sum(f['demand'] for f in coverage_plan)} kW"
    )
    st.write(
        ", ".join(f["name"] for f in coverage_plan)
        or "No facilities restored"
    )

st.divider()
# ---------------- RESTORATION PLAN ----------------

st.header("Restoration Plan")

plan = make_plan(FACILITIES, available)

df = create_plan_table(
    FACILITIES,
    plan,
    available
)

supplied = int(df["Supplied (kW)"].sum())
shortage = max(0, total_demand - supplied)
unused_power = max(0, available - supplied)

m1, m2, m3 = st.columns(3)

m1.metric("Power allocated", f"{supplied} kW")
m2.metric("Unmet demand", f"{shortage} kW")
m3.metric("Unused available power", f"{unused_power} kW")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

# ---------------- LIVE FACILITY STATUS ----------------

st.subheader("⚡ Live Facility Status")

status_cols = st.columns(3)

for i, (_, facility) in enumerate(df.iterrows()):
    is_powered = (
        facility["Supplied (kW)"] >= facility["Demand (kW)"]
        and facility["Demand (kW)"] > 0
    )

    with status_cols[i % 3]:
        if is_powered:
            st.success(
                f"🟢 {facility['Facility']} — POWERED"
            )
        else:
            st.error(
                f"🔴 {facility['Facility']} — NOT RESTORED"
            )

# ---------------- MICROGRID NETWORK ----------------

st.subheader("⚡ Live Microgrid Network")

hospital_powered = any(
    f["name"] == "Hospital" for f in plan
)
water_powered = any(
    f["name"] == "Water Pump" for f in plan
)
mobile_powered = any(
    f["name"] == "Mobile Tower" for f in plan
)
shelter_powered = any(
    f["name"] == "Emergency Shelter" for f in plan
)

def node_status(powered):
    return "🟢 POWERED" if powered else "🔴 OFFLINE"

network_html = f"""
<div style="
    background:linear-gradient(135deg,#101D33,#142944);
    padding:22px;
    border-radius:16px;
    border:1px solid #28506B;
    color:#EAF4FF;
    text-align:center;
">
    <div style="
        display:flex;
        justify-content:space-around;
        flex-wrap:wrap;
        gap:12px;
    ">
        <div style="background:#1A3550;padding:18px;border-radius:12px;min-width:130px;">
            ☀️ <b>SOLAR</b><br>
            {actual_solar} kW
        </div>
        <div style="background:#1A3550;padding:18px;border-radius:12px;min-width:130px;">
            🔋 <b>BATTERY</b><br>
            {actual_battery} kW
        </div>
    </div>
    <div style="font-size:25px;color:#55D6FF;padding:10px;">↓</div>
    <div style="
        background:#16445B;
        border:1px solid #55D6FF;
        padding:18px;
        border-radius:12px;
        font-size:18px;
    ">
        ⚡ <b>GRIDRESCUE CONTROLLER</b><br>
        Allocating {available} kW
    </div>
    <div style="font-size:25px;color:#55D6FF;padding:10px;">↓</div>
    <div style="
        display:grid;
        grid-template-columns:repeat(auto-fit,minmax(145px,1fr));
        gap:12px;
    ">
        <div style="background:#1A3550;padding:14px;border-radius:10px;">
            🏥 Hospital<br>{node_status(hospital_powered)}
        </div>
        <div style="background:#1A3550;padding:14px;border-radius:10px;">
            💧 Water Pump<br>{node_status(water_powered)}
        </div>
        <div style="background:#1A3550;padding:14px;border-radius:10px;">
            📡 Mobile Tower<br>{node_status(mobile_powered)}
        </div>
        <div style="background:#1A3550;padding:14px;border-radius:10px;">
            🏠 Emergency Shelter<br>{node_status(shelter_powered)}
        </div>
    </div>
</div>
"""

st.markdown(network_html, unsafe_allow_html=True)

st.caption(
    "Network diagram is a software simulation, not a connection "
    "to physical electrical equipment."
)

# ---------------- RESCUE REPLAY ----------------

st.header("🔁 Rescue Replay")

st.write(
    "Compare the normal restoration plan with the plan after "
    "the selected blackout event."
)

before_plan = make_plan(FACILITIES, normal_power)
after_plan = make_plan(FACILITIES, available)

before = create_plan_table(
    FACILITIES,
    before_plan,
    normal_power
)

after = create_plan_table(
    FACILITIES,
    after_plan,
    available
)

comparison = before[
    ["Facility", "Supplied (kW)"]
].merge(
    after[["Facility", "Supplied (kW)"]],
    on="Facility",
    suffixes=(" before", " after")
)

comparison["Change (kW)"] = (
    comparison["Supplied (kW) after"]
    - comparison["Supplied (kW) before"]
)

st.caption(f"Selected event: {failure_event}")

r1, r2, r3 = st.columns(3)

r1.metric("Normal power", f"{normal_power} kW")
r2.metric("Power after event", f"{available} kW")
r3.metric(
    "Power lost",
    f"{max(0, normal_power - available)} kW"
)

st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True
)

if failure_event == "No failure":
    st.info(
        "No failure is active. Select a blackout event in the "
        "sidebar to replay a disruption."
    )
elif available < normal_power:
    st.warning(
        f"The event reduced available power by "
        f"{normal_power - available} kW. "
        "GridRescue recalculated the restoration plan."
    )
else:
    st.info(
        "The selected event did not reduce the available power "
        "with the current slider settings."
    )

# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "GRIDRESCUE | Adaptive Blackout Restoration Prototype | "
    "Results are simulated for demonstration."
)
