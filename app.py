```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="International Debt Analysis",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 International Debt Analysis Dashboard")
st.markdown("### Python • Exploratory Data Analysis (EDA) • SQL • Interactive Visualization")

st.markdown("""
This project analyzes international debt indicators across countries
and compares available values for 2020 and 2024.
""")

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

    # Identify important columns
    country_col = next(
        (c for c in df.columns if c.lower() in ["country_name", "country name"]),
        None
    )

    indicator_col = next(
        (c for c in df.columns if c.lower() in ["series_name", "series name"]),
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

    # Sidebar filters
    st.sidebar.header("Dashboard Filters")

    countries = sorted(
        df[country_col].dropna().astype(str).unique().tolist()
    )

    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        countries,
        default=["India"] if "India" in countries else countries[:1]
    )

    filtered_df = df[
        df[country_col].astype(str).isin(selected_countries)
    ].copy()

    st.subheader("📊 Dataset Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Records", f"{len(filtered_df):,}")
    col2.metric(
        "Countries Selected",
        str(filtered_df[country_col].nunique())
    )
    col3.metric(
        "Unique Debt Indicators",
        f"{filtered_df[indicator_col].nunique():,}"
    )

    st.divider()

    # Exploratory Data Analysis
    st.subheader("🔍 Exploratory Data Analysis (EDA)")

    eda1, eda2 = st.columns(2)

    with eda1:
        st.markdown("**Records by Country**")

        country_counts = (
            filtered_df[country_col]
            .value_counts()
            .head(10)
            .reset_index()
        )

        country_counts.columns = ["Country", "Record Count"]

        fig_country = px.bar(
            country_counts,
            x="Country",
            y="Record Count",
            title="Top 10 Countries by Record Count"
        )

        st.plotly_chart(fig_country, use_container_width=True)

    with eda2:
        st.markdown("**Top 10 Debt Indicators**")

        indicator_counts = (
            filtered_df[indicator_col]
            .value_counts()
            .head(10)
            .reset_index()
        )

        indicator_counts.columns = ["Debt Indicator", "Record Count"]

        fig_indicator = px.bar(
            indicator_counts,
            x="Record Count",
            y="Debt Indicator",
            orientation="h",
            title="Top 10 Indicators by Record Count"
        )

        st.plotly_chart(fig_indicator, use_container_width=True)

    # Compare 2020 and 2024
    st.divider()
    st.subheader("📈 Debt Indicator Comparison: 2020 vs 2024")

    if "2020" in filtered_df.columns and "2024" in filtered_df.columns:

        comparison = filtered_df[
            [country_col, indicator_col, "2020", "2024"]
        ].copy()

        comparison = comparison.dropna(subset=["2020", "2024"])

        if not comparison.empty:

            st.caption(
                "Only indicators with available values in both years are included. "
                "Values from different indicators may have different units and "
                "should not be interpreted as a single total debt figure."
            )

            selected_indicator = st.selectbox(
                "Select Debt Indicator",
                sorted(
                    comparison[indicator_col]
                    .dropna()
                    .astype(str)
                    .unique()
                )
            )

            indicator_data = comparison[
                comparison[indicator_col].astype(str) == selected_indicator
            ]

            fig_comparison = px.bar(
                indicator_data,
                x=country_col,
                y=["2020", "2024"],
                barmode="group",
                title=f"{selected_indicator}: 2020 vs 2024",
                labels={
                    "value": "Indicator Value",
                    "variable": "Year",
                    country_col: "Country"
                }
            )

            st.plotly_chart(
                fig_comparison,
                use_container_width=True
            )

            st.markdown("**Comparison Data**")

            st.dataframe(
                indicator_data[
                    [country_col, indicator_col, "2020", "2024"]
                ],
                use_container_width=True
            )

            # Change percentage
            valid_data = indicator_data[
                (indicator_data["2020"] != 0)
                & indicator_data["2020"].notna()
                & indicator_data["2024"].notna()
            ].copy()

            if not valid_data.empty:
                valid_data["Change (%)"] = (
                    (valid_data["2024"] - valid_data["2020"])
                    / valid_data["2020"]
                ) * 100

                st.markdown("**Percentage Change by Country**")

                st.dataframe(
                    valid_data[
                        [country_col, "2020", "2024", "Change (%)"]
                    ].round(2),
                    use_container_width=True
                )

        else:
            st.warning(
                "No records have values for both 2020 and 2024 "
                "under the current country selection."
            )

    else:
        st.warning("The dataset must contain both 2020 and 2024 columns.")

    # Missing value analysis
    st.divider()
    st.subheader("🧹 Missing Value Analysis")

    missing_count = filtered_df.isna().sum()

    missing_df = (
        missing_count[missing_count > 0]
        .sort_values(ascending=False)
        .head(15)
        .reset_index()
    )

    missing_df.columns = ["Column", "Missing Values"]

    if not missing_df.empty:
        fig_missing = px.bar(
            missing_df,
            x="Column",
            y="Missing Values",
            title="Top 15 Columns with Missing Values"
        )

        st.plotly_chart(fig_missing, use_container_width=True)
    else:
        st.success("No missing values found in the selected data.")

    # View data
    st.divider()
    st.subheader("📋 Filtered Dataset")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=400
    )

    # Download filtered data
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
        "Upload International_Debt_Cleaned.csv to the GitHub repository "
        "in the same folder as app.py."
    )

except Exception as e:
    st.error(f"An error occurred: {e}")
```
