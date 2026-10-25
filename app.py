import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="International Debt Analysis",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 International Debt Analysis Dashboard")
st.markdown("### Python • EDA • SQL • Interactive Visualization")

st.sidebar.header("Dashboard Filters")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv(
        "International_Debt_Cleaned.csv",
        encoding="latin1"
    )

try:
    df = load_data()

    # Clean column names
    df.columns = df.columns.astype(str).str.strip()

    # Find important columns
    country_col = next(
        (
            c for c in df.columns
            if c.lower().strip() in ["country_name", "country name"]
        ),
        None
    )

    indicator_col = next(
        (
            c for c in df.columns
            if c.lower().strip() in ["series_name", "series name"]
        ),
        None
    )

    if country_col is None or indicator_col is None:
        st.error("Country Name or Series Name column was not found.")
        st.write("Available columns:", df.columns.tolist())
        st.stop()

    # Convert year columns to numeric
    for year in ["2020", "2024"]:
        if year in df.columns:
            df[year] = pd.to_numeric(df[year], errors="coerce")

    # Sidebar country selection
    countries = sorted(
        df[country_col].dropna().astype(str).unique().tolist()
    )

    selected_countries = st.sidebar.multiselect(
        "Select Countries to Compare",
        options=countries,
        default=countries[:2] if len(countries) >= 2 else countries
    )

    # Filter dataset
    if selected_countries:
        filtered_df = df[
            df[country_col].astype(str).isin(selected_countries)
        ].copy()
    else:
        filtered_df = df.copy()

    # Overview
    st.subheader("📊 Dataset Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Records", f"{len(df):,}")

    with col2:
        st.metric(
            "Countries",
            df[country_col].nunique()
        )

    with col3:
        st.metric(
            "Debt Indicators",
            df[indicator_col].nunique()
        )

    st.divider()

    # Country-wise record count
    st.subheader("🌎 Country-wise Records")

    country_counts = (
        filtered_df.groupby(country_col)
        .size()
        .reset_index(name="Record Count")
    )

    if not country_counts.empty:
        fig_country = px.bar(
            country_counts,
            x=country_col,
            y="Record Count",
            color=country_col,
            title="Records by Selected Country"
        )

        st.plotly_chart(
            fig_country,
            use_container_width=True
        )
    else:
        st.info("Please select at least one country.")

    st.divider()

    # Indicator selection
    st.subheader("📈 Compare Debt Indicators: 2020 vs 2024")

    if "2020" in filtered_df.columns and "2024" in filtered_df.columns:

        comparison = filtered_df[
            [country_col, indicator_col, "2020", "2024"]
        ].copy()

        comparison["2020"] = pd.to_numeric(
            comparison["2020"], errors="coerce"
        )

        comparison["2024"] = pd.to_numeric(
            comparison["2024"], errors="coerce"
        )

        # Remove missing values, but keep valid zero values
        comparison = comparison.dropna(
            subset=["2020", "2024"]
        )

        indicators = sorted(
            comparison[indicator_col]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if indicators:
            selected_indicator = st.selectbox(
                "Select Debt Indicator",
                options=indicators
            )

            indicator_data = comparison[
                comparison[indicator_col].astype(str)
                == selected_indicator
            ].copy()

            if not indicator_data.empty:

                st.caption(
                    "Compare the same indicator across countries. "
                    "A value of zero is retained if it exists in the source data. "
                    "Missing values are not converted to zero."
                )

                # Display comparison table
                st.markdown("#### Comparison Data")

                st.dataframe(
                    indicator_data.rename(
                        columns={
                            country_col: "Country Name",
                            indicator_col: "Series Name"
                        }
                    ),
                    use_container_width=True
                )

                # Grouped chart
                chart_data = indicator_data.melt(
                    id_vars=[country_col],
                    value_vars=["2020", "2024"],
                    var_name="Year",
                    value_name="Indicator Value"
                )

                fig_compare = px.bar(
                    chart_data,
                    x=country_col,
                    y="Indicator Value",
                    color="Year",
                    barmode="group",
                    title=f"{selected_indicator}: 2020 vs 2024",
                    labels={
                        country_col: "Country",
                        "Indicator Value": "Indicator Value"
                    },
                    barmode_group_gap=0.15
                )

                st.plotly_chart(
                    fig_compare,
                    use_container_width=True
                )

                # Percentage change for each country
                st.markdown("#### Percentage Change by Country")

                change_data = indicator_data.copy()

                change_data["Change (%)"] = (
                    (
                        change_data["2024"] - change_data["2020"]
                    )
                    / change_data["2020"].replace(0, float("nan"))
                ) * 100

                change_data = change_data.rename(
                    columns={
                        country_col: "Country Name",
                        indicator_col: "Series Name"
                    }
                )

                st.dataframe(
                    change_data[
                        [
                            "Country Name",
                            "Series Name",
                            "2020",
                            "2024",
                            "Change (%)"
                        ]
                    ].round(2),
                    use_container_width=True
                )

                st.caption(
                    "Percentage change is unavailable when the 2020 value is zero. "
                    "Different indicators may have different units; "
                    "do not add unlike indicators together as one debt total."
                )

            else:
                st.warning(
                    "No comparable records are available for this indicator."
                )

        else:
            st.warning(
                "No indicators with values in both 2020 and 2024 were found."
            )

    else:
        st.warning(
            "The dataset does not contain both 2020 and 2024 columns."
        )

    st.divider()

    # Filtered dataset
    st.subheader("📋 Filtered Dataset")

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    # Download filtered dataset
    csv_data = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv_data,
        file_name="International_Debt_Filtered.csv",
        mime="text/csv"
    )

    st.success("Dashboard loaded successfully!")

    st.caption(
        "International Debt Analysis Project | Python, EDA, SQL and Streamlit"
    )

except FileNotFoundError:
    st.error("Dataset file not found.")

    st.info(
        "Upload International_Debt_Cleaned.csv to the same GitHub repository "
        "as app.py."
    )

except Exception as e:
    st.error(f"An error occurred: {e}")

