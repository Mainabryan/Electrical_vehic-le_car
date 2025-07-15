import asyncio
import platform
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pdfkit

FPS = 60

async def main():
    # Setup - Initialize data and UI
    st.title("Electric Vehicle Price vs Range Analysis")
    st.write("Educating users on high-price, low-range EVs for better decision-making.")

    # 1. Dataset Loading
    uploaded_file = st.file_uploader("Upload your EV dataset (CSV)", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        # Preload default dataset (replace with your GitHub URL or local path)
        df = pd.read_csv('Electric_cars_dataset(1).csv')  # Adjust path as needed

    # Basic data prep from notebook
    df = df[['Model Year', 'Make', 'Electric Range', 'Expected Price ($1k)']].dropna()

    # 7. Summary Stats Panel
    st.header("Key Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Average Range (miles)", int(df['Electric Range'].mean()))
    with col2:
        st.metric("Average Price ($1k)", round(df['Expected Price ($1k)'].mean(), 2))

    # 3. Filters / Inputs (Sidebar)
    st.sidebar.header("Filters")
    brand = st.sidebar.selectbox("Select Brand", options=['All'] + sorted(df['Make'].unique().tolist()))
    model_year = st.sidebar.slider("Model Year", int(df['Model Year'].min()), int(df['Model Year'].max()), int(df['Model Year'].max()))
    price_range = st.sidebar.slider("Price Range ($1k)", float(df['Expected Price ($1k)'].min()), float(df['Expected Price ($1k)'].max()), (0, 100))
    range_miles = st.sidebar.slider("Range (miles)", int(df['Electric Range'].min()), int(df['Electric Range'].max()), (0, 300))
    show_outliers = st.sidebar.checkbox("Show Outliers", value=True)
    advanced_charts = st.sidebar.checkbox("Show Advanced Charts", value=False)

    # Filter data
    filtered_df = df[(df['Model Year'] <= model_year) &
                     (df['Expected Price ($1k)'].between(price_range[0], price_range[1])) &
                     (df['Electric Range'].between(range_miles[0], range_miles[1]))]
    if brand != 'All':
        filtered_df = filtered_df[filtered_df['Make'] == brand]

    # Outlier handling (simple IQR method)
    if not show_outliers:
        Q1 = filtered_df['Expected Price ($1k)'].quantile(0.25)
        Q3 = filtered_df['Expected Price ($1k)'].quantile(0.75)
        IQR = Q3 - Q1
        filtered_df = filtered_df[~((filtered_df['Expected Price ($1k)'] < (Q1 - 1.5 * IQR)) | (filtered_df['Expected Price ($1k)'] > (Q3 + 1.5 * IQR)))]

    # 2. Interactive Visualizations
    st.header("Visualizations")
    # Strip plot by Model Year, Price per Mile
    fig1, ax1 = plt.subplots()
    filtered_df['Price per Mile'] = filtered_df['Expected Price ($1k)'] * 1000 / filtered_df['Electric Range'].replace(0, 1)  # Avoid division by zero
    sns.stripplot(data=filtered_df, x='Model Year', y='Price per Mile', ax=ax1)
    ax1.set_title("Price per Mile by Model Year")
    st.pyplot(fig1)

    # Heatmap of Price vs Range
    fig2, ax2 = plt.subplots()
    pivot = filtered_df.pivot_table(values='Expected Price ($1k)', index='Electric Range', columns='Model Year', aggfunc='mean')
    sns.heatmap(pivot, ax=ax2, cmap='YlOrRd')
    ax2.set_title("Price vs Range Heatmap")
    st.pyplot(fig2)

    # Optional Scatter with Hover Tooltips (Plotly)
    if advanced_charts:
        fig3 = px.scatter(filtered_df, x='Electric Range', y='Expected Price ($1k)', color='Make',
                         hover_data=['Model Year', 'Make'], title="Price vs Range with Tooltips")
        st.plotly_chart(fig3)

    # 4. Insight Panel
    st.header("Business Insights")
    with st.expander("Business Recommendations"):
        st.markdown("""
        - 🚗 **Target Education**: High-price, low-range EVs (e.g., >$40k, <100 miles) need buyer education on value.
        - 💡 **Dealer Strategy**: Offer incentives for low-range models to boost sales.
        - 📈 **Manufacturer Focus**: Adjust MSRP for better range-price balance.
        """)
    with st.expander("Final Thoughts"):
        st.markdown("This analysis highlights the need for transparent pricing to retain EV customers. 🎯")

    # 5. Export Feature
    st.header("Export Data")
    csv = filtered_df.to_csv(index=False)
    st.download_button(label="Download Filtered Data (CSV)", data=csv, file_name="ev_filtered_data.csv", mime="text/csv")
    # Bonus PDF export (requires pdfkit config)
    html_content = filtered_df.to_html()
    pdf = pdfkit.from_string(html_content, False)  # Configure pdfkit path if needed
    st.download_button(label="Download Insights (PDF)", data=pdf, file_name="ev_insights.pdf", mime="application/pdf")

    # 6. Branding
    st.markdown("---")
    st.markdown("Created by Maina Bryan, aspiring Data Scientist | Connect on [LinkedIn URL](https://www.linkedin.com/in/yourprofile)")

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())