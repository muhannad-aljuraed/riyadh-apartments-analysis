"""لوحة Streamlit لتحليل بيانات شقق الرياض."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_FILE = Path(__file__).resolve().parent / "riyadh_apartments_data.csv"
CURRENCY = "ر.س"


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)
    df["Price per sqm (SAR)"] = df["Selling Price (SAR)"] / df["Area (sqm)"]
    return df


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("🔍 الفلاتر")

    regions = st.sidebar.multiselect(
        "المنطقة",
        sorted(df["Region"].unique()),
        default=sorted(df["Region"].unique()),
    )
    neighborhoods = st.sidebar.multiselect(
        "الحي",
        sorted(df["Neighborhood"].unique()),
        default=sorted(df["Neighborhood"].unique()),
    )
    bedrooms = st.sidebar.multiselect(
        "عدد الغرف",
        sorted(df["Bedrooms"].unique()),
        default=sorted(df["Bedrooms"].unique()),
    )
    furnished = st.sidebar.multiselect(
        "التأثيث",
        sorted(df["Furnished"].unique()),
        default=sorted(df["Furnished"].unique()),
    )
    elevator = st.sidebar.multiselect(
        "المصعد",
        sorted(df["Elevator"].unique()),
        default=sorted(df["Elevator"].unique()),
    )

    min_price = int(df["Selling Price (SAR)"].min())
    max_price = int(df["Selling Price (SAR)"].max())
    price_range = st.sidebar.slider(
        "نطاق السعر (ريال سعودي)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=10_000,
    )

    min_area = int(df["Area (sqm)"].min())
    max_area = int(df["Area (sqm)"].max())
    area_range = st.sidebar.slider(
        "نطاق المساحة (م²)",
        min_value=min_area,
        max_value=max_area,
        value=(min_area, max_area),
    )

    filtered = df[
        df["Region"].isin(regions)
        & df["Neighborhood"].isin(neighborhoods)
        & df["Bedrooms"].isin(bedrooms)
        & df["Furnished"].isin(furnished)
        & df["Elevator"].isin(elevator)
        & df["Selling Price (SAR)"].between(price_range[0], price_range[1])
        & df["Area (sqm)"].between(area_range[0], area_range[1])
    ]
    st.sidebar.info(f"عدد الشقق بعد التصفية: {len(filtered):,}")
    return filtered


def format_currency(value: float) -> str:
    return f"{value:,.0f} {CURRENCY}"


def render_summary(df: pd.DataFrame) -> None:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("عدد الشقق", f"{len(df):,}")
    col2.metric("متوسط السعر", format_currency(df["Selling Price (SAR)"].mean()))
    col3.metric("متوسط المساحة", f"{df['Area (sqm)'].mean():.0f} م²")
    col4.metric("متوسط سعر المتر", format_currency(df["Price per sqm (SAR)"].mean()))
    col5.metric("متوسط الغرف", f"{df['Bedrooms'].mean():.1f}")


def render_charts(df: pd.DataFrame) -> None:
    st.subheader("📊 الرسوم البيانية")

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        fig_price = px.histogram(
            df,
            x="Selling Price (SAR)",
            nbins=40,
            title="توزيع أسعار البيع",
            labels={"Selling Price (SAR)": "السعر (ريال سعودي)", "count": "العدد"},
            color_discrete_sequence=["#2563eb"],
        )
        fig_price.update_layout(template="plotly_white", height=420)
        st.plotly_chart(fig_price, use_container_width=True)

    with row1_col2:
        fig_scatter = px.scatter(
            df,
            x="Area (sqm)",
            y="Selling Price (SAR)",
            color="Bedrooms",
            title="العلاقة بين المساحة والسعر",
            labels={
                "Area (sqm)": "المساحة (م²)",
                "Selling Price (SAR)": "السعر (ريال سعودي)",
                "Bedrooms": "عدد الغرف",
            },
            hover_data=["Neighborhood", "Region", "Furnished"],
            color_continuous_scale="Viridis",
        )
        fig_scatter.update_layout(template="plotly_white", height=420)
        st.plotly_chart(fig_scatter, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        region_counts = df["Region"].value_counts().reset_index()
        region_counts.columns = ["Region", "Count"]
        fig_region = px.bar(
            region_counts,
            x="Region",
            y="Count",
            title="عدد الشقق حسب المنطقة",
            labels={"Region": "المنطقة", "Count": "عدد الشقق"},
            color="Count",
            color_continuous_scale="Blues",
        )
        fig_region.update_layout(template="plotly_white", height=420, showlegend=False)
        st.plotly_chart(fig_region, use_container_width=True)

    with row2_col2:
        bedroom_avg = (
            df.groupby("Bedrooms", as_index=False)["Selling Price (SAR)"]
            .mean()
            .sort_values("Bedrooms")
        )
        fig_bedrooms = px.bar(
            bedroom_avg,
            x="Bedrooms",
            y="Selling Price (SAR)",
            title="متوسط السعر حسب عدد الغرف",
            labels={"Bedrooms": "عدد الغرف", "Selling Price (SAR)": "متوسط السعر"},
            color="Selling Price (SAR)",
            color_continuous_scale="Greens",
        )
        fig_bedrooms.update_layout(template="plotly_white", height=420, showlegend=False)
        st.plotly_chart(fig_bedrooms, use_container_width=True)

    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        top_neighborhoods = (
            df.groupby("Neighborhood", as_index=False)["Selling Price (SAR)"]
            .mean()
            .sort_values("Selling Price (SAR)", ascending=False)
            .head(10)
        )
        fig_neighborhoods = px.bar(
            top_neighborhoods,
            x="Selling Price (SAR)",
            y="Neighborhood",
            orientation="h",
            title="أعلى 10 أحياء من حيث متوسط السعر",
            labels={"Selling Price (SAR)": "متوسط السعر", "Neighborhood": "الحي"},
            color="Selling Price (SAR)",
            color_continuous_scale="Oranges",
        )
        fig_neighborhoods.update_layout(template="plotly_white", height=420, showlegend=False)
        st.plotly_chart(fig_neighborhoods, use_container_width=True)

    with row3_col2:
        bedroom_counts = df["Bedrooms"].value_counts().sort_index().reset_index()
        bedroom_counts.columns = ["Bedrooms", "Count"]
        bedroom_counts["Bedrooms"] = bedroom_counts["Bedrooms"].astype(str)
        fig_pie = px.pie(
            bedroom_counts,
            names="Bedrooms",
            values="Count",
            title="توزيع الشقق حسب عدد الغرف",
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig_pie.update_layout(height=420)
        st.plotly_chart(fig_pie, use_container_width=True)

    row4_col1, row4_col2 = st.columns(2)
    with row4_col1:
        elevator_avg = (
            df.groupby("Elevator", as_index=False)["Selling Price (SAR)"]
            .mean()
            .sort_values("Elevator")
        )
        fig_elevator = px.bar(
            elevator_avg,
            x="Elevator",
            y="Selling Price (SAR)",
            title="متوسط السعر حسب وجود المصعد",
            labels={"Elevator": "المصعد", "Selling Price (SAR)": "متوسط السعر"},
            color="Elevator",
            color_discrete_map={"Yes": "#16a34a", "No": "#dc2626"},
        )
        fig_elevator.update_layout(template="plotly_white", height=420, showlegend=False)
        st.plotly_chart(fig_elevator, use_container_width=True)

    with row4_col2:
        age_price = (
            df.groupby("Property Age (years)", as_index=False)["Price per sqm (SAR)"]
            .mean()
            .sort_values("Property Age (years)")
        )
        fig_age = px.line(
            age_price,
            x="Property Age (years)",
            y="Price per sqm (SAR)",
            markers=True,
            title="متوسط سعر المتر حسب عمر العقار",
            labels={
                "Property Age (years)": "عمر العقار (سنوات)",
                "Price per sqm (SAR)": "سعر المتر (ريال)",
            },
        )
        fig_age.update_layout(template="plotly_white", height=420)
        st.plotly_chart(fig_age, use_container_width=True)


def render_statistics(df: pd.DataFrame) -> None:
    st.subheader("📈 إحصائيات تفصيلية")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**إحصائيات السعر**")
        st.write(f"الحد الأدنى: {format_currency(df['Selling Price (SAR)'].min())}")
        st.write(f"الحد الأقصى: {format_currency(df['Selling Price (SAR)'].max())}")
        st.write(f"الوسيط: {format_currency(df['Selling Price (SAR)'].median())}")
        st.write(f"الانحراف المعياري: {format_currency(df['Selling Price (SAR)'].std())}")

    with col2:
        st.markdown("**إحصائيات المساحة**")
        st.write(f"الحد الأدنى: {df['Area (sqm)'].min():.0f} م²")
        st.write(f"الحد الأقصى: {df['Area (sqm)'].max():.0f} م²")
        st.write(f"الوسيط: {df['Area (sqm)'].median():.0f} م²")
        st.write(f"الانحراف المعياري: {df['Area (sqm)'].std():.0f} م²")

    with col3:
        total = len(df)
        furnished_count = (df["Furnished"] == "Yes").sum()
        elevator_count = (df["Elevator"] == "Yes").sum()
        st.markdown("**معلومات إضافية**")
        st.write(f"شقق مؤثثة: {furnished_count:,} ({furnished_count / total * 100:.1f}%)")
        st.write(f"شقق بمصعد: {elevator_count:,} ({elevator_count / total * 100:.1f}%)")
        st.write(f"متوسط عمر العقار: {df['Property Age (years)'].mean():.1f} سنة")
        st.write(f"عدد الأحياء: {df['Neighborhood'].nunique():,}")


def main() -> None:
    st.set_page_config(
        page_title="تحليل شقق الرياض",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
            [data-testid="stVerticalBlockContainer"], 
            [data-testid="stMetric"],
            .stTabs {
                direction: rtl;
                text-align: right;
            }
            
            [data-testid="stSidebarContent"] {
                direction: ltr;
                text-align: right;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("🏢 لوحة تحليل شقق الرياض")
    st.caption("تحليل تفاعلي لـ 10,000 إعلان شقة في مدينة الرياض")

    if not DATA_FILE.exists():
        st.error(f"لم يتم العثور على ملف البيانات: {DATA_FILE}")
        st.stop()

    df = load_data()
    filtered_df = apply_filters(df)

    st.divider()
    render_summary(filtered_df)

    if filtered_df.empty:
        st.warning("لا توجد بيانات مطابقة للفلاتر المحددة. عدّل الفلاتر من الشريط الجانبي.")
        st.stop()

    st.divider()
    render_charts(filtered_df)

    st.divider()
    st.subheader("📋 البيانات المفلترة")
    display_columns = [
        "Region",
        "Neighborhood",
        "Area (sqm)",
        "Bedrooms",
        "Bathrooms",
        "Elevator",
        "Furnished",
        "Property Age (years)",
        "Selling Price (SAR)",
        "Price per sqm (SAR)",
    ]
    st.dataframe(
        filtered_df[display_columns].sort_values("Selling Price (SAR)", ascending=False),
        use_container_width=True,
        height=400,
    )

    st.divider()
    render_statistics(filtered_df)


if __name__ == "__main__":
    main()
