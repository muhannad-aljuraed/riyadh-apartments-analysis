import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# إعدادات الصفحة والتنسيق الجديد المعدل
st.set_page_config(
    page_title="لوحة تحليل شقق الرياض",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنسيق RTL الكامل لإصلاح الفلاتر والقائمة الجانبية

st.markdown("""
    <style>
        .stApp {
            direction: rtl;
        }
        [data-testid="stSidebar"] {
            min-width: 300px !important;
            direction: rtl;
        }
        * {
            text-align: right !important;
        }
    </style>
""", unsafe_allow_html=True)

# تحميل البيانات
@st.cache_data
def load_data():
    df = pd.read_csv('riyadh_apartments_data.csv')
    return df

df = load_data()

# العنوان الرئيسي
st.title("🏢 لوحة تحليل شقق الرياض")
st.markdown("---")

# عرض معلومات عامة عن البيانات
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("عدد الشقق", f"{len(df):,}")

with col2:
    avg_price = df['Selling Price (SAR)'].mean()
    st.metric("متوسط السعر", f"₪{avg_price:,.0f}")

with col3:
    max_price = df['Selling Price (SAR)'].max()
    st.metric("أعلى سعر", f"₪{max_price:,.0f}")

with col4:
    avg_area = df['Area (sqm)'].mean()
    st.metric("متوسط المساحة", f"{avg_area:.0f} متر²")

with col5:
    avg_bedrooms = df['Bedrooms'].mean()
    st.metric("متوسط الغرف", f"{avg_bedrooms:.1f}")

st.markdown("---")

# الفلاتر في الشريط الجانبي
st.sidebar.title("🔍 الفلاتر")

# فلتر المنطقة
regions = st.sidebar.multiselect(
    "اختر المنطقة:",
    df['Region'].unique(),
    default=df['Region'].unique()
)

# فلتر نطاق السعر
price_range = st.sidebar.slider(
    "نطاق السعر (ريال سعودي):",
    min_value=int(df['Selling Price (SAR)'].min()),
    max_value=int(df['Selling Price (SAR)'].max()),
    value=(int(df['Selling Price (SAR)'].min()), int(df['Selling Price (SAR)'].max())),
    step=50000
)

# فلتر عدد الغرف
bedrooms = st.sidebar.multiselect(
    "عدد الغرف:",
    sorted(df['Bedrooms'].unique()),
    default=sorted(df['Bedrooms'].unique())
)

# فلتر المصعد
elevator_filter = st.sidebar.multiselect(
    "المصعد:",
    df['Elevator'].unique(),
    default=df['Elevator'].unique()
)

# تطبيق الفلاتر
filtered_df = df[
    (df['Region'].isin(regions)) &
    (df['Selling Price (SAR)'].between(price_range[0], price_range[1])) &
    (df['Bedrooms'].isin(bedrooms)) &
    (df['Elevator'].isin(elevator_filter))
]

# عرض عدد الشقق المفلترة
st.sidebar.info(f"عدد الشقق المفلترة: {len(filtered_df)}")

st.markdown("### 📊 الرسوم البيانية")

# صف أول من الرسوم البيانية
col1, col2 = st.columns(2)

# رسم بياني 1: توزيع الأسعار
with col1:
    fig_price = px.histogram(
        filtered_df,
        x='Selling Price (SAR)',
        nbins=40,
        title="توزيع الأسعار",
        labels={'Selling Price (SAR)': 'السعر (ريال سعودي)', 'count': 'العدد'},
        color_discrete_sequence=['#1f77b4']
    )
    fig_price.update_layout(
        hovermode='x unified',
        xaxis_title="السعر (ريال سعودي)",
        yaxis_title="عدد الشقق",
        template="plotly_white",
        height=400
    )
    st.plotly_chart(fig_price, use_container_width=True)

# رسم بياني 2: العلاقة بين المساحة والسعر
with col2:
    fig_scatter = px.scatter(
        filtered_df,
        x='Area (sqm)',
        y='Selling Price (SAR)',
        color='Bedrooms',
        size='Bedrooms',
        title="العلاقة بين المساحة والسعر",
        labels={'Area (sqm)': 'المساحة (متر²)', 'Selling Price (SAR)': 'السعر (ريال سعودي)', 'Bedrooms': 'الغرف'},
        hover_data=['Neighborhood', 'Region'],
        color_continuous_scale="Viridis"
    )
    fig_scatter.update_layout(
        hovermode='closest',
        template="plotly_white",
        height=400
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# صف ثاني من الرسوم البيانية
col1, col2 = st.columns(2)

# رسم بياني 3: عدد الشقق حسب المنطقة
with col1:
    region_counts = filtered_df['Region'].value_counts().sort_values(ascending=True)
    fig_region = px.bar(
        x=region_counts.values,
        y=region_counts.index,
        orientation='h',
        title="عدد الشقق حسب المنطقة",
        labels={'x': 'عدد الشقق', 'y': 'المنطقة'},
        color=region_counts.values,
        color_continuous_scale="Blues"
    )
    fig_region.update_layout(
        template="plotly_white",
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_region, use_container_width=True)

# رسم بياني 4: متوسط السعر حسب عدد الغرف
with col2:
    bedroom_avg = filtered_df.groupby('Bedrooms')['Selling Price (SAR)'].mean().sort_index()
    fig_bedroom = px.bar(
        x=bedroom_avg.index,
        y=bedroom_avg.values,
        title="متوسط السعر حسب عدد الغرف",
        labels={'x': 'عدد الغرف', 'y': 'متوسط السعر (ريال سعودي)'},
        color=bedroom_avg.values,
        color_continuous_scale="Greens"
    )
    fig_bedroom.update_layout(
        template="plotly_white",
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_bedroom, use_container_width=True)

# صف ثالث من الرسوم البيانية
col1, col2 = st.columns(2)

# رسم بياني 5: تأثير المصعد على السعر
with col1:
    elevator_avg = filtered_df.groupby('Elevator')['Selling Price (SAR)'].agg(['mean', 'count']).reset_index()
    fig_elevator = px.bar(
        elevator_avg,
        x='Elevator',
        y='mean',
        title="متوسط السعر حسب وجود المصعد",
        labels={'Elevator': 'المصعد', 'mean': 'متوسط السعر (ريال سعودي)'},
        color='Elevator',
        color_discrete_map={'Yes': '#2ecc71', 'No': '#e74c3c'}
    )
    fig_elevator.update_layout(
        template="plotly_white",
        height=400,
        showlegend=False
    )
    st.plotly_chart(fig_elevator, use_container_width=True)

# رسم بياني 6: توزيع الشقق حسب عدد الغرف
with col2:
    bedroom_counts = filtered_df['Bedrooms'].value_counts().sort_index()
    fig_pie = px.pie(
        values=bedroom_counts.values,
        names=bedroom_counts.index,
        title="توزيع الشقق حسب عدد الغرف",
        labels={'names': 'عدد الغرف'},
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie.update_layout(
        height=400
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# جدول البيانات
st.markdown("### 📋 البيانات المفلترة")
st.dataframe(
    filtered_df.sort_values('Selling Price (SAR)', ascending=False),
    use_container_width=True,
    height=400
)

# إحصائيات إضافية
st.markdown("---")
st.markdown("### 📈 الإحصائيات التفصيلية")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("إحصائيات السعر")
    st.write(f"الحد الأدنى: ر.س{filtered_df['Selling Price (SAR)'].min():,.0f}")
    st.write(f"الحد الأقصى: ر.س{filtered_df['Selling Price (SAR)'].max():,.0f}")
    st.write(f"الوسيط: ر.س{filtered_df['Selling Price (SAR)'].median():,.0f}")
    st.write(f"الانحراف المعياري:ر.س {filtered_df['Selling Price (SAR)'].std():,.0f}")

with col2:
    st.subheader("إحصائيات المساحة")
    st.write(f"الحد الأدنى: {filtered_df['Area (sqm)'].min():.0f} متر²")
    st.write(f"الحد الأقصى: {filtered_df['Area (sqm)'].max():.0f} متر²")
    st.write(f"الوسيط: {filtered_df['Area (sqm)'].median():.0f} متر²")
    st.write(f"الانحراف المعياري: {filtered_df['Area (sqm)'].std():.0f} متر²")

with col3:
    st.subheader("معلومات إضافية")
    furnished = len(filtered_df[filtered_df['Furnished'] == 'Yes'])
    st.write(f"شقق مؤثثة: {furnished} ({furnished/len(filtered_df)*100:.1f}%)")
    with_elevator = len(filtered_df[filtered_df['Elevator'] == 'Yes'])
    st.write(f"شقق بمصعد: {with_elevator} ({with_elevator/len(filtered_df)*100:.1f}%)")
    avg_age = filtered_df['Property Age (years)'].mean()
    st.write(f"متوسط عمر العقار: {avg_age:.1f} سنة")
