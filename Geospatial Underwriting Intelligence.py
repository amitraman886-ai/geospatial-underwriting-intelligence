import streamlit as st
import requests
from datetime import datetime, timedelta

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Geospatial Underwriting Intelligence",
    layout="wide"
)

# ======================================================
# CUSTOM CSS
# ======================================================

st.markdown("""
<style>

/* Main container */
.block-container {
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}

/* Main title */
.main-title {
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 18px;
}

/* Section header */
.section-header {
    font-size: 24px;
    font-weight: 600;
    margin-top: 18px;
    margin-bottom: 8px;
}

/* Sub header */
.sub-header {
    font-size: 18px;
    font-weight: 600;
    margin-top: 12px;
    margin-bottom: 4px;
}

/* Standard text */
.standard-text {
    font-size: 16px;
    line-height: 1.5;
}

/* Compact metric card */
.metric-card {
    background-color: #ffffff;
    padding: 6px 0px;
}

.metric-label {
    font-size: 14px;
    color: #666666;
    margin-bottom: 2px;
}

.metric-value {
    font-size: 20px;
    font-weight: 600;
    color: #111111;
}

/* Insight box */
.insight-box {
    background-color: #f7f9fc;
    padding: 8px 14px;
    border-radius: 10px;
    border: 1px solid #e6e9ef;
    margin-top: 6px;
    margin-bottom: 10px;
}

/* Bullet spacing */
.insight-box ul {
    margin-top: 0px;
    margin-bottom: 0px;
    padding-left: 20px;
}

.insight-box li {
    margin-bottom: 4px;
    font-size: 16px;
}

/* Divider */
hr {
    margin-top: 12px;
    margin-bottom: 12px;
    border: none;
    border-top: 1px solid #e5e7eb;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# TITLE
# ======================================================

st.markdown("""
<div class="main-title">
Geospatial Underwriting Intelligence
</div>

<div class="standard-text" style="margin-top:-10px; color:#666666;">
A geospatial underwriting intelligence tool for area-level risk assessment
</div>
""", unsafe_allow_html=True)

# ======================================================
# INPUT
# ======================================================

postcode_input = st.text_input("Enter UK Postcode")

# ======================================================
# SESSION STATE
# ======================================================

if "lat" not in st.session_state:
    st.session_state.lat = None
    st.session_state.lon = None
    st.session_state.postcode = None
    st.session_state.region = None

# ======================================================
# BUTTON
# ======================================================

if st.button("Analyze Area"):

    if postcode_input:

        postcode = postcode_input.strip().upper().replace(" ", "")

        st.session_state.lat = None
        st.session_state.lon = None

        url = f"https://api.postcodes.io/postcodes/{postcode}"
        res = requests.get(url).json()

        if res["status"] == 200:

            st.session_state.lat = res["result"]["latitude"]
            st.session_state.lon = res["result"]["longitude"]
            st.session_state.postcode = postcode
            st.session_state.region = res["result"]["region"]

        else:
            st.error("Invalid postcode")

# ======================================================
# MAIN
# ======================================================

if st.session_state.lat:

    lat = st.session_state.lat
    lon = st.session_state.lon
    postcode = st.session_state.postcode
    region = st.session_state.region

    # ======================================================
    # RISK ENGINE VARIABLES
    # ======================================================

    risk_score = 0
    risk_drivers = []

    heat_days = 0
    heavy_rain_days = 0

    st.success(f"Location Loaded: {postcode}")

    # ======================================================
    # WEATHER RISK
    # ======================================================

    st.markdown(
        '<div class="section-header">Weather Risk</div>',
        unsafe_allow_html=True
    )

    start_year = 2022
    end_year = 2024

    st.markdown(
        f'<div class="standard-text"><b>Data Period:</b> {start_year} - {end_year}</div>',
        unsafe_allow_html=True
    )

    try:

        with st.spinner("Analyzing weather data..."):

            all_temp_max = []
            all_temp_min = []
            all_wind = []
            all_rain = []
            all_humidity = []

            for year in range(start_year, end_year + 1):

                url = (
                    f"https://archive-api.open-meteo.com/v1/archive?"
                    f"latitude={lat}&longitude={lon}"
                    f"&start_date={year}-01-01"
                    f"&end_date={year}-12-31"
                    f"&daily=temperature_2m_max,"
                    f"temperature_2m_min,"
                    f"windspeed_10m_max,"
                    f"precipitation_sum,"
                    f"relative_humidity_2m_mean"
                    f"&timezone=auto"
                )

                res = requests.get(url)

                if res.status_code == 200:

                    data = res.json().get("daily", {})

                    all_temp_max += data.get("temperature_2m_max", [])
                    all_temp_min += data.get("temperature_2m_min", [])
                    all_wind += data.get("windspeed_10m_max", [])
                    all_rain += data.get("precipitation_sum", [])
                    all_humidity += data.get(
                        "relative_humidity_2m_mean", []
                    )

        if all_temp_max:

            avg_temp = sum(all_temp_max + all_temp_min) / (
                len(all_temp_max) + len(all_temp_min)
            )

            max_temp = max(all_temp_max)
            min_temp = min(all_temp_min)

            avg_wind = sum(all_wind) / len(all_wind)

            total_rain = sum(all_rain) / (
                end_year - start_year + 1
            )

            avg_humidity = sum(all_humidity) / len(all_humidity)

            col1, col2, col3, col4, col5 = st.columns(5)

            metrics = [
                ("Avg Temp", f"{round(avg_temp, 2)} °C"),
                ("Max Temp", f"{max_temp} °C"),
                ("Min Temp", f"{min_temp} °C"),
                ("Avg Wind", f"{round(avg_wind, 2)} km/h"),
                ("Annual Rainfall", f"{round(total_rain, 1)} mm")
            ]

            for col, (label, value) in zip(
                [col1, col2, col3, col4, col5],
                metrics
            ):

                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value">{value}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # ======================================================
            # WEATHER EXTREMES
            # ======================================================

            st.markdown(
                '<div class="sub-header">Weather Extremes</div>',
                unsafe_allow_html=True
            )

            heat_days = len([
                t for t in all_temp_max if t > 30
            ])

            freezing_days = len([
                t for t in all_temp_min if t < 0
            ])

            heavy_rain_days = len([
                r for r in all_rain if r > 20
            ])

            high_wind_days = len([
                w for w in all_wind if w > 50
            ])

            st.markdown(f"""
            <div class="standard-text">
            <ul>
                <li>Days Above 30°C: {heat_days}</li>
                <li>Freezing Days Below 0°C: {freezing_days}</li>
                <li>Heavy Rain Days Above 20mm: {heavy_rain_days}</li>
                <li>High Wind Days Above 50 km/h: {high_wind_days}</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

            # ======================================================
            # WEATHER INSIGHTS
            # ======================================================

            insights = []

            if heat_days > 10:
                insights.append(
                    "Potential heat stress and material degradation exposure."
                )
                risk_score += 10
                risk_drivers.append("Elevated heat exposure")

            if freezing_days > 20:
                insights.append(
                    "Potential pipe freezing exposure."
                )
                risk_score += 15
                risk_drivers.append("High freezing frequency")

            if heavy_rain_days > 5:
                insights.append(
                    "Potential surface water accumulation exposure."
                )
                risk_score += 15
                risk_drivers.append("Elevated rainfall exposure")

            if heavy_rain_days > 15:
                insights.append(
                    "Elevated rainfall intensity exposure."
                )

            if high_wind_days > 3:
                insights.append(
                    "Moderate wind exposure."
                )

            if high_wind_days > 10:
                insights.append(
                    "Elevated structural and roof damage exposure."
                )
                risk_score += 15
                risk_drivers.append("High wind exposure")

            if avg_humidity > 80:
                insights.append(
                    "Potential damp and mould exposure."
                )
                risk_score += 10
                risk_drivers.append("Elevated humidity exposure")

            st.markdown(
                '<div class="sub-header">Key Insights</div>',
                unsafe_allow_html=True
            )

            if insights:

                insight_html = "".join(
                    [f"<li>{i}</li>" for i in insights]
                )

                st.markdown(f"""
                <div class="insight-box">
                    <ul>
                        {insight_html}
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            else:
                st.success("No major weather concerns identified.")

    except Exception as e:

        st.error("Weather analysis failed.")
        st.write(e)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ======================================================
    # CRIME RISK
    # ======================================================

    st.markdown(
        '<div class="section-header">Crime Risk</div>',
        unsafe_allow_html=True
    )

    try:

        with st.spinner("Analyzing crime data..."):

            url = (
                f"https://data.police.uk/api/crimes-street/all-crime?"
                f"lat={lat}&lng={lon}"
            )

            res = requests.get(url)

            last_month = 0
            crime_types = {}

            if res.status_code == 200:

                crimes = res.json()

                last_month = len(crimes)

                for c in crimes:

                    cat = c.get("category", "other")

                    crime_types[cat] = (
                        crime_types.get(cat, 0) + 1
                    )

            yearly = 0

            for i in range(12):

                date = (
                    datetime.today().replace(day=1)
                    - timedelta(days=30 * i)
                )

                date_str = date.strftime("%Y-%m")

                url = (
                    f"https://data.police.uk/api/crimes-street/all-crime?"
                    f"lat={lat}&lng={lon}&date={date_str}"
                )

                r = requests.get(url)

                if r.status_code == 200:
                    yearly += len(r.json())

        col1, col2 = st.columns(2)

        crime_metrics = [
            ("Last Month", last_month),
            ("Last 12 Months", yearly)
        ]

        for col, (label, value) in zip(
            [col1, col2],
            crime_metrics
        ):

            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(
            '<div class="sub-header">Crime Breakdown</div>',
            unsafe_allow_html=True
        )

        if crime_types:

            crime_html = ""

            for k, v in sorted(
                crime_types.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]:

                crime_html += (
                    f"<li>{k.replace('-', ' ').title()}: {v}</li>"
                )

            st.markdown(f"""
            <div class="standard-text">
                <ul>
                    {crime_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        insights = []

        if crime_types.get("burglary", 0) > 20:
            insights.append(
                "Elevated burglary exposure."
            )
            risk_score += 20
            risk_drivers.append("Elevated burglary exposure")

        if crime_types.get(
            "criminal-damage-arson", 0
        ) > 10:
            insights.append(
                "Potential arson and fire exposure."
            )
            risk_score += 15
            risk_drivers.append("Potential arson exposure")

        if last_month > 300:
            insights.append(
                "Elevated recent crime frequency."
            )
            risk_score += 20
            risk_drivers.append("High recent crime frequency")

        st.markdown(
            '<div class="sub-header">Key Insights</div>',
            unsafe_allow_html=True
        )

        if insights:

            insight_html = "".join(
                [f"<li>{i}</li>" for i in insights]
            )

            st.markdown(f"""
            <div class="insight-box">
                <ul>
                    {insight_html}
                </ul>
                </div>
            """, unsafe_allow_html=True)

        else:
            st.success("No major crime concerns identified.")

    except Exception as e:

        st.error("Crime analysis failed.")
        st.write(e)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ======================================================
    # AREA RISK
    # ======================================================

    st.markdown(
        '<div class="section-header">Area Risk</div>',
        unsafe_allow_html=True
    )

    avg_prices = {
        "London": 650000,
        "South East": 450000,
        "North West": 220000,
        "Scotland": 200000,
    }

    value = avg_prices.get(region, 250000)

    if region == "London":

        density = "High"

        insights = [
            "Higher accumulation risk.",
            "Elevated fire spread exposure.",
            "Potential emergency access constraints.",
            "Higher insured value exposure."
        ]

        risk_score += 15
        risk_drivers.append("High urban accumulation exposure")

    elif region in ["South East", "North West"]:

        density = "Moderate / Mixed"

        insights = [
            "Moderate accumulation exposure.",
            "Reduced fire spread potential.",
            "Stable overall exposure profile.",
            "Moderate insured value exposure."
        ]

        risk_score += 8

    else:

        density = "Low / Mixed"

        insights = [
            "Lower accumulation exposure.",
            "Greater environmental loss sensitivity.",
            "Possible extended emergency response times.",
            "Lower insured value exposure."
        ]

    col1, col2 = st.columns(2)

    area_metrics = [
        ("Urban Density", density),
        ("Avg Property Value", f"£{value:,}")
    ]

    for col, (label, value) in zip(
        [col1, col2],
        area_metrics
    ):

        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(
        '<div class="sub-header">Key Insights</div>',
        unsafe_allow_html=True
    )

    insight_html = "".join(
        [f"<li>{i}</li>" for i in insights]
    )

    st.markdown(f"""
    <div class="insight-box">
        <ul>
            {insight_html}
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ======================================================
    # FLOOD RISK
    # ======================================================

    st.markdown(
        '<div class="section-header">Flood Risk</div>',
        unsafe_allow_html=True
    )

    try:

        elev_url = (
            f"https://api.open-meteo.com/v1/elevation?"
            f"latitude={lat}&longitude={lon}"
        )

        elev_res = requests.get(elev_url)

        if elev_res.status_code == 200:

            elevation = elev_res.json()["elevation"][0]

            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Elevation</div>
                <div class="metric-value">{elevation} m</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(
                '<div class="sub-header">Key Insights</div>',
                unsafe_allow_html=True
            )

            flood_insights = []

            if elevation < 10:

                flood_insights.append(
                    "Low elevation may indicate increased flood susceptibility."
                )

                risk_score += 20
                risk_drivers.append("Potential flood susceptibility")

            else:

                flood_insights.append(
                    "No immediate low-elevation flood concern identified."
                )

            insight_html = "".join(
                [f"<li>{i}</li>" for i in flood_insights]
            )

            st.markdown(f"""
            <div class="insight-box">
                <ul>
                    {insight_html}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.warning("Elevation data unavailable.")

    except Exception as e:

        st.warning("Flood analysis failed.")
        st.write(e)

    # ======================================================
    # GROUND & SUBSIDENCE RISK
    # ======================================================

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-header">Ground & Subsidence Risk</div>',
        unsafe_allow_html=True
    )

    try:

        soil_url = (
            f"https://rest.isric.org/soilgrids/v2.0/properties/query?"
            f"lat={lat}&lon={lon}"
            f"&property=clay"
            f"&depth=0-5cm"
            f"&value=mean"
        )

        soil_res = requests.get(soil_url)

        clay_content = None

        if soil_res.status_code == 200:

            soil_data = soil_res.json()

            layers = soil_data.get(
                "properties", {}
            ).get("layers", [])

            if layers:

                depths = layers[0].get("depths", [])

                if depths:

                    clay_content = (
                        depths[0]
                        .get("values", {})
                        .get("mean")
                    )

        soil_type = "Mixed Soil"
        subsidence_sensitivity = "Moderate"
        heave_potential = "Moderate"

        subsidence_insights = []

        if clay_content is not None:

            clay_content = clay_content / 10

            if clay_content >= 45:

                soil_type = "Shrinkable Clay Soil"
                subsidence_sensitivity = "Elevated"
                heave_potential = "Elevated"

                risk_score += 20
                risk_drivers.append(
                    "Shrinkable clay ground conditions"
                )

                subsidence_insights.append(
                    "Clay-rich ground conditions identified."
                )

                subsidence_insights.append(
                    "Shrink-swell soil movement susceptibility may be elevated."
                )

                if heat_days > 10:

                    subsidence_insights.append(
                        "Prolonged dry weather may contribute to soil shrinkage and foundation movement."
                    )

                    risk_score += 10

                if heavy_rain_days > 10:

                    subsidence_insights.append(
                        "Rainfall variability may contribute to heave exposure."
                    )

                    risk_score += 5

            elif clay_content >= 30:

                soil_type = "Clay-Rich Soil"
                subsidence_sensitivity = "Moderate"
                heave_potential = "Moderate"

                risk_score += 10

                subsidence_insights.append(
                    "Moderate clay concentration identified."
                )

                subsidence_insights.append(
                    "Seasonal moisture variation may affect ground stability."
                )

            elif clay_content >= 15:

                soil_type = "Mixed Mineral Soil"
                subsidence_sensitivity = "Low"
                heave_potential = "Low"

                subsidence_insights.append(
                    "No significant shrink-swell soil indicators identified."
                )

            else:

                soil_type = "Sand / Gravel Dominant Soil"
                subsidence_sensitivity = "Low"
                heave_potential = "Low"

                subsidence_insights.append(
                    "Lower shrink-swell susceptibility identified."
                )

                subsidence_insights.append(
                    "Potential erosion or settlement exposure may still exist."
                )

        else:

            subsidence_insights.append(
                "Soil composition data unavailable."
            )

        col1, col2, col3, col4 = st.columns(4)

        metrics = [
            ("Indicative Soil Type", soil_type),
            (
                "Clay Content",
                f"{round(clay_content, 1)}%"
                if clay_content is not None
                else "Unavailable"
            ),
            (
                "Subsidence Sensitivity",
                subsidence_sensitivity
            ),
            ("Heave Potential", heave_potential)
        ]

        for col, (label, value) in zip(
            [col1, col2, col3, col4],
            metrics
        ):

            with col:

                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(
            '<div class="sub-header">Key Insights</div>',
            unsafe_allow_html=True
        )

        insight_html = "".join(
            [f"<li>{i}</li>" for i in subsidence_insights]
        )

        st.markdown(f"""
        <div class="insight-box">
            <ul>
                {insight_html}
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            '<div class="sub-header">Underwriting Considerations</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="insight-box">
            <ul>
                <li>Subsidence and heave are strongly influenced by soil moisture variability.</li>
                <li>Tree and shrub root activity may increase moisture extraction exposure.</li>
                <li>Heavy rainfall following prolonged dry periods may contribute to heave conditions.</li>
                <li>Leaking drains and poor drainage conditions may weaken ground stability.</li>
                <li>Seasonal wet-dry cycles may increase foundation movement susceptibility.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:

        st.warning("Ground and subsidence analysis failed.")
        st.write(e)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ======================================================
    # UNDERWRITING SUMMARY
    # ======================================================

    if risk_score <= 30:
        risk_level = "Low"

    elif risk_score <= 60:
        risk_level = "Moderate"

    elif risk_score <= 80:
        risk_level = "Elevated"

    else:
        risk_level = "High"

    summary_parts = []

    if risk_score > 60:

        summary_parts.append(
            "The location demonstrates elevated overall underwriting exposure."
        )

    elif risk_score > 30:

        summary_parts.append(
            "The location demonstrates moderate underwriting exposure."
        )

    else:

        summary_parts.append(
            "The location demonstrates generally low underwriting exposure."
        )

    if "Elevated rainfall exposure" in risk_drivers:

        summary_parts.append(
            "Rainfall intensity and water accumulation indicators are notable."
        )

    if "High freezing frequency" in risk_drivers:

        summary_parts.append(
            "Freezing exposure may increase escape of water susceptibility."
        )

    if "Elevated burglary exposure" in risk_drivers:

        summary_parts.append(
            "Crime-related exposure indicators are elevated."
        )

    if "Potential flood susceptibility" in risk_drivers:

        summary_parts.append(
            "Low elevation may contribute to flood sensitivity."
        )

    if "Shrinkable clay ground conditions" in risk_drivers:

        summary_parts.append(
            "Ground conditions indicate elevated subsidence susceptibility."
        )

    executive_summary = " ".join(summary_parts)

    st.markdown(
        '<div class="section-header">Exposure Summary</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Composite Risk Index</div>
            <div class="metric-value">{risk_score}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Risk Classification</div>
            <div class="metric-value">{risk_level}</div>
        </div>
        """, unsafe_allow_html=True)
    

# ======================================================
# VISUAL RISK BADGE
# ======================================================

    if risk_level == "Low":
        badge_color = "#2e7d32"
        badge_bg = "#e8f5e9"

    elif risk_level == "Moderate":
        badge_color = "#f9a825"
        badge_bg = "#fff8e1"

    elif risk_level == "Elevated":
        badge_color = "#ef6c00"
        badge_bg = "#fff3e0"

    else:
        badge_color = "#c62828"
        badge_bg = "#ffebee"

    st.markdown(f"""
    <div style="
    display:inline-block;
    padding:8px 18px;
    border-radius:20px;
    background-color:{badge_bg};
    color:{badge_color};
    font-weight:600;
    font-size:16px;
    margin-top:10px;
    ">
    Risk Level: {risk_level}
    </div>
    """, unsafe_allow_html=True)

    # ======================================================
    # TOP RISK DRIVERS
    # ======================================================

    st.markdown(
        '<div class="sub-header">Top Risk Drivers</div>',
        unsafe_allow_html=True
    )

    unique_drivers = list(dict.fromkeys(risk_drivers))

    driver_html = "".join(
        [f"<li>{d}</li>" for d in unique_drivers[:5]]
    )

    st.markdown(f"""
    <div class="insight-box">
        <ul>
            {driver_html}
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # ======================================================
    # EXECUTIVE SUMMARY
    # ======================================================

    st.markdown(
        '<div class="sub-header">Executive Underwriting Summary</div>',
        unsafe_allow_html=True
    )

    st.markdown(f"""
    <div class="insight-box">
        <div class="standard-text">
            {executive_summary}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ======================================================
    # SUGGESTED UNDERWRITING CONSIDERATIONS
    # ======================================================

    st.markdown(
        '<div class="sub-header" style="color:#0f4c81;">Suggested Underwriting Considerations</div>',
        unsafe_allow_html=True
    )

    underwriting_considerations = []

    # ======================================================
    # FLOOD CONSIDERATIONS
    # ======================================================

    if "Potential flood susceptibility" in risk_drivers:
        underwriting_considerations.append(
            "Consider reviewing flood resilience measures and prior flood history."
        )

    # ======================================================
    # SUBSIDENCE CONSIDERATIONS
    # ======================================================

    if "Shrinkable clay ground conditions" in risk_drivers:

        underwriting_considerations.append(
            "Consider reviewing prior subsidence history and structural movement indicators."
        )

        underwriting_considerations.append(
            "Assess proximity of large trees and vegetation near foundations."
        )

    # ======================================================
    # WEATHER CONSIDERATIONS
    # ======================================================

    if "High freezing frequency" in risk_drivers:
        underwriting_considerations.append(
            "Review escape of water protections and winter maintenance controls."
        )

    if "Elevated rainfall exposure" in risk_drivers:
        underwriting_considerations.append(
            "Consider drainage performance and surface water management exposure."
        )

    if "High wind exposure" in risk_drivers:
        underwriting_considerations.append(
            "Review roof condition and external structural resilience."
        )

    # ======================================================
    # CRIME CONSIDERATIONS
    # ======================================================

    if "Elevated burglary exposure" in risk_drivers:
        underwriting_considerations.append(
            "Assess theft protection and physical security measures."
        )

    if "Potential arson exposure" in risk_drivers:
        underwriting_considerations.append(
            "Consider local fire protection and property security arrangements."
        )

    # ======================================================
    # AREA RISK CONSIDERATIONS
    # ======================================================

    if "High urban accumulation exposure" in risk_drivers:
        underwriting_considerations.append(
            "Consider accumulation exposure and neighbouring property density."
        )

    # ======================================================
    # DEFAULT RESPONSE
    # ======================================================

    if not underwriting_considerations:
        underwriting_considerations.append(
            "No significant additional underwriting considerations identified based on available location intelligence."
        )

    # ======================================================
    # DISPLAY CONSIDERATIONS
    # ======================================================

    consideration_html = "".join(
        [f"<li>{c}</li>" for c in underwriting_considerations]
    )

    st.markdown(f"""
    <div class="insight-box" style="
        background-color:#eaf4ff;
        border:1px solid #c7def5;
    ">
        <ul>
            {consideration_html}
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # ======================================================
    # RISK METHODOLOGY
    # ======================================================

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-header">Risk Methodology</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="insight-box">

    <div class="standard-text">
    This assessment is based on geospatial and environmental intelligence derived from publicly available datasets.
    </div>

    <br>

    <div class="standard-text">
    The composite risk index is a relative exposure indicator derived from weighted environmental and geospatial risk factors.
    </div>

    <br>

    <div class="standard-text">
    Higher scores indicate elevated relative underwriting exposure.
    </div>

    <br>

    <div class="standard-text">
    The platform evaluates indicative exposure factors including:
    </div>

    <ul>
        <li>Weather patterns and climate indicators</li>
        <li>Crime activity trends</li>
        <li>Flood susceptibility indicators</li>
        <li>Ground and subsidence conditions</li>
        <li>Regional accumulation exposure</li>
    </ul>

    <div class="standard-text">
    Risk scores are intended to support underwriting triage and exposure awareness only.
    </div>

    <br>

    <div class="standard-text">
    The assessment does not evaluate:
    </div>

    <ul>
        <li>Actual property construction details</li>
        <li>Security protections</li>
        <li>Building condition</li>
        <li>Claims history</li>
        <li>Property-specific flood resilience measures</li>
    </ul>

    <div class="standard-text">
    Final underwriting decisions should incorporate property-level underwriting information and insurer risk appetite.
    </div>

    </div>
    """, unsafe_allow_html=True)

    # ======================================================
    # DATA SOURCES
    # ======================================================

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-header">Data Sources</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="insight-box">
        <ul>
            <li>Weather Risk: Open-Meteo Historical Weather</li>
            <li>Crime Risk: UK Police Data</li>
            <li>Flood Risk: Open Elevation Data</li>
            <li>Ground & Subsidence Risk: SoilGrids</li>
            <li>Postcode & Geolocation: Postcodes.io</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

