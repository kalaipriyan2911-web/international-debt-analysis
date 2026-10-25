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

@st.cache_data
def load_data():
    return pd.read_csv("International_Debt_Cleaned.csv", encoding="latin1")

try:
    df = load_data()

    st.success("Dataset loaded successfully!")

    st.subheader("📊 Dataset Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Records", f"{len(df):,}")

    with col2:
        st.metric("Total Columns", len(df.columns))

    with col3:
        st.metric(
            "Countries",
            df["Country Name"].nunique()
            if "Country Name" in df.columns
            else df["country_name"].nunique()
            if "country_name" in df.columns
            else "N/A"
        )

    st.subheader("🔎 Explore Dataset")
    st.dataframe(df.head(100), use_container_width=True)

    st.subheader("🌐 Country Analysis")

    country_col = next(
        (c for c in ["Country Name", "country_name"] if c in df.columns),
        None
    )

    if country_col:
        countries = sorted(df[country_col].dropna().unique())
        selected_country = st.selectbox("Select Country", countries)

        country_df = df[df[country_col] == selected_country]
        st.write(f"Selected Country: **{selected_country}**")
        st.dataframe(country_df, use_container_width=True)

    st.subheader("📈 Missing Values Analysis")

    missing = df.isnull().sum().sort_values(ascending=False)
    missing = missing[missing > 0]

    if not missing.empty:
        missing_df = missing.reset_index()
        missing_df.columns = ["Column", "Missing Values"]

        fig = px.bar(
            missing_df.head(15),
            x="Column",
            y="Missing Values",
            title="Top 15 Columns with Missing Values"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No missing values found.")

    st.subheader("📊 Numeric Data Distribution")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if numeric_cols:
        selected_column = st.selectbox(
            "Select a numeric column",
            numeric_cols
        )

        fig = px.histogram(
            df,
            x=selected_column,
            title=f"Distribution of {selected_column}"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📥 Download Dataset")

    st.download_button(
        "Download CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="International_Debt_Cleaned.csv",
        mime="text/csv"
    )

except Exception as e:
        st.subheader("📊 Debt Indicators: 2020 vs 2024")

    if "2020" in df.columns and "2024" in df.columns:
        year_data = df.copy()

        year_data["2020"] = pd.to_numeric(
            year_data["2020"], errors="coerce"
        )
        year_data["2024"] = pd.to_numeric(
            year_data["2024"], errors="coerce"
        )

        indicator_col = next(
            (c for c in ["Series Name", "series_name"] if c in df.columns),
            None
        )

        country_col = next(
            (c for c in ["Country Name", "country_name"] if c in df.columns),
            None
        )

        if country_col and indicator_col:
            country_options = sorted(
                year_data[country_col].dropna().unique()
            )
            selected = st.selectbox(
                "Choose country for comparison",
                country_options,
                key="comparison_country"
            )

            comparison = year_data[
                year_data[country_col] == selected
            ][[indicator_col, "2020", "2024"]].copy()

            comparison = comparison.dropna(
                subset=["2020", "2024"]
            ).head(20)

            if not comparison.empty:
                chart_data = comparison.melt(
                    id_vars=indicator_col,
                    value_vars=["2020", "2024"],
                    var_name="Year",
                    value_name="Indicator Value"
                )

                fig = px.bar(
                    chart_data,
                    x=indicator_col,
                    y="Indicator Value",
                    color="Year",
                    barmode="group",
                    title=f"{selected}: 2020 vs 2024"
                )

                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(comparison, use_container_width=True)
            else:
                st.warning(
                    "No comparable 2020 and 2024 values for this country."
                )
    else:
        st.warning("The dataset does not contain both 2020 and 2024 columns.")
    st.error(f"Unable to load dataset: {e}")
    st.info("Check that International_Debt_Cleaned.csv exists in the repository.")

st.caption("International Debt Analysis Project | Python, EDA, SQL & Streamlit")
