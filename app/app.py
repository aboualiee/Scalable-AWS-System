import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import boto3
from io import StringIO

# Check if statsmodels is available
try:
    import statsmodels
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Student Performance Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup S3 client
s3 = boto3.client('s3')
S3_BUCKET = 'student-performance-app-files'
S3_FILE_KEY = 'StudentPerformanceFactors.csv'

# Function to handle data loading
@st.cache_data
def load_data(uploaded_file=None):
    # Case 1: User uploaded a file
    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file)
            st.success("Successfully loaded uploaded file!")
            return data
        except Exception as e:
            st.error(f"Error loading uploaded file: {e}")
    
    # Case 2: Load from S3
    try:
        # Get the object from S3
        response = s3.get_object(Bucket=S3_BUCKET, Key=S3_FILE_KEY)
        # Read the data as bytes and convert to DataFrame
        data = pd.read_csv(StringIO(response['Body'].read().decode('utf-8')))
        st.success("Successfully loaded data from S3!")
        return data
    except Exception as e:
        st.error(f"Error loading data from S3: {e}")
        return None

# Main application
st.title("📊 Student Performance Analytics Dashboard")
st.markdown("Analyze factors influencing student performance and identify key insights.")

# Sidebar for data upload and filters
with st.sidebar:
    st.header("Data Source & Filters")
    
    # File uploader for optional upload
    uploaded_file = st.file_uploader("Upload your own CSV file (optional)", type=['csv'])
    
    # Load data
    data = load_data(uploaded_file)
    
    # Only show filters if data is loaded
    if data is not None:
        st.subheader("Analysis Filters")
        
        # Get categorical columns for filtering
        categorical_cols = data.select_dtypes(include=['object']).columns.tolist()
        
        # Add filters for categorical variables if available
        filter_selections = {}
        for col in categorical_cols[:3]:  # Limit to first 3 categorical columns to avoid cluttering
            if len(data[col].unique()) < 10:  # Only for columns with reasonable number of categories
                filter_selections[col] = st.multiselect(
                    f"Filter by {col.replace('_', ' ')}:",
                    options=sorted(data[col].unique()),
                    default=[]
                )
        
        # Apply filters to data
        filtered_data = data.copy()
        for col, selected_values in filter_selections.items():
            if selected_values:
                filtered_data = filtered_data[filtered_data[col].isin(selected_values)]
        
        # Show filter summary
        if filtered_data.shape[0] != data.shape[0]:
            st.info(f"Filtered data: {filtered_data.shape[0]} of {data.shape[0]} records ({(filtered_data.shape[0]/data.shape[0])*100:.1f}%)")
        
        # Additional options
        st.subheader("Display Options")
        show_details = st.checkbox("Show detailed statistics", value=False)
    else:
        filtered_data = None

# Main content area - Only proceed if data is loaded
if filtered_data is not None:
    # Tabs for organized analysis
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "📊 Performance Analysis", "🔍 Factor Impact", "📈 Relationship Explorer"])
    
    # Tab 1: Dataset Overview
    with tab1:
        st.header("Dataset Overview")
        
        # Row 1: Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if 'Exam_Score' in filtered_data.columns:
                st.metric("Average Score", f"{filtered_data['Exam_Score'].mean():.1f}", 
                         f"{filtered_data['Exam_Score'].mean() - data['Exam_Score'].mean():.1f}")
        with col2:
            if 'Exam_Score' in filtered_data.columns:
                pass_rate = (filtered_data['Exam_Score'] >= 60).mean() * 100
                overall_pass_rate = (data['Exam_Score'] >= 60).mean() * 100
                st.metric("Pass Rate", f"{pass_rate:.1f}%", f"{pass_rate - overall_pass_rate:.1f}%")
        with col3:
            st.metric("Total Students", f"{filtered_data.shape[0]}")
        with col4:
            if 'Exam_Score' in filtered_data.columns:
                st.metric("Score Range", f"{filtered_data['Exam_Score'].min()} - {filtered_data['Exam_Score'].max()}")
        
        # Row 2: Data preview and stats
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Data Preview")
            st.dataframe(filtered_data.head(), use_container_width=True)
        with col2:
            st.subheader("Data Quality")
            # Missing values summary
            missing_values = filtered_data.isnull().sum()
            missing_percent = (missing_values / len(filtered_data)) * 100
            missing_df = pd.DataFrame({
                'Missing Values': missing_values,
                'Percent': missing_percent
            })
            missing_df = missing_df[missing_df['Missing Values'] > 0]
            
            if not missing_df.empty:
                st.dataframe(missing_df, use_container_width=True)
            else:
                st.success("No missing values found in the dataset!")
        
        # Row 3: Column Information
        if show_details:
            st.subheader("Column Information")
            # Create two DataFrames for numerical and categorical columns
            numerical_info = filtered_data.describe().transpose()
            categorical_cols = filtered_data.select_dtypes(include=['object']).columns
            categorical_info = pd.DataFrame({
                'Type': filtered_data[categorical_cols].dtypes,
                'Unique Values': [filtered_data[col].nunique() for col in categorical_cols],
                'Most Common': [filtered_data[col].value_counts().index[0] if not filtered_data[col].value_counts().empty else None for col in categorical_cols]
            })
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("Numerical Columns")
                st.dataframe(numerical_info, use_container_width=True)
            with col2:
                st.write("Categorical Columns")
                st.dataframe(categorical_info, use_container_width=True)
    
    # Tab 2: Performance Analysis
    with tab2:
        st.header("Student Performance Analysis")
        
        # Performance distribution
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Exam Score Distribution")
            if 'Exam_Score' in filtered_data.columns:
                fig = px.histogram(filtered_data, x='Exam_Score', nbins=20, 
                                  marginal="box", 
                                  color_discrete_sequence=['#3498db'],
                                  title="Distribution of Exam Scores")
                fig.update_layout(xaxis_title="Exam Score", yaxis_title="Count")
                st.plotly_chart(fig, use_container_width=True)
                
        with col2:
            st.subheader("Performance Categories")
            if 'Exam_Score' in filtered_data.columns:
                # Create performance categories
                def categorize_performance(score):
                    if score >= 90:
                        return 'Excellent (90-100)'
                    elif score >= 80:
                        return 'Very Good (80-89)'
                    elif score >= 70:
                        return 'Good (70-79)'
                    elif score >= 60:
                        return 'Satisfactory (60-69)'
                    else:
                        return 'Needs Improvement (<60)'
                
                filtered_data['Performance_Category'] = filtered_data['Exam_Score'].apply(categorize_performance)
                category_counts = filtered_data['Performance_Category'].value_counts().reset_index()
                category_counts.columns = ['Category', 'Count']
                # Sort in logical order
                order = ['Excellent (90-100)', 'Very Good (80-89)', 'Good (70-79)', 
                        'Satisfactory (60-69)', 'Needs Improvement (<60)']
                category_counts['Category'] = pd.Categorical(category_counts['Category'], categories=order, ordered=True)
                category_counts = category_counts.sort_values('Category')
                
                fig = px.pie(category_counts, values='Count', names='Category', 
                           title="Student Performance Categories")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
        
        # Performance by categories
        st.subheader("Performance Across Categories")
        
        if filtered_data.select_dtypes(include=['object']).columns.size > 0:
            col1, col2 = st.columns([1, 3])
            with col1:
                selected_cat = st.selectbox("Select Category:", 
                                          filtered_data.select_dtypes(include=['object']).columns.tolist())
            with col2:
                if 'Exam_Score' in filtered_data.columns:
                    # Calculate mean and count by category
                    summary_df = filtered_data.groupby(selected_cat)['Exam_Score'].agg(['mean', 'count']).reset_index()
                    summary_df.columns = [selected_cat, 'Average Score', 'Count']
                    summary_df = summary_df.sort_values('Average Score', ascending=False)
                    
                    fig = px.bar(summary_df, x=selected_cat, y='Average Score',
                               text='Average Score',
                               hover_data=['Count'],
                               color='Average Score',
                               color_continuous_scale=px.colors.sequential.Bluyl,
                               title=f"Average Exam Score by {selected_cat.replace('_', ' ')}")
                    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
                    st.plotly_chart(fig, use_container_width=True)
        
        # Boxplot comparison
        if 'Exam_Score' in filtered_data.columns and len(categorical_cols) > 0:
            st.subheader("Score Distribution by Category")
            selected_cat = st.selectbox("Select Category for Detailed View:", 
                                      categorical_cols,
                                      key="boxplot_category")
            
            # Check if the selected category has a reasonable number of unique values
            if filtered_data[selected_cat].nunique() <= 10:
                fig = px.box(filtered_data, x=selected_cat, y='Exam_Score',
                           color=selected_cat,
                           title=f"Exam Score Distribution by {selected_cat.replace('_', ' ')}")
                fig.update_layout(xaxis_title=selected_cat.replace('_', ' '), 
                                yaxis_title="Exam Score")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"Too many unique values in {selected_cat} for a meaningful visualization.")
    
    # Tab 3: Factor Impact Analysis - UPDATED SECTION
    with tab3:
        st.header("Factor Impact Analysis")
        
        # Only proceed if Exam_Score exists
        if 'Exam_Score' in filtered_data.columns:
            # Get numerical columns excluding Exam_Score
            numerical_cols = [col for col in filtered_data.select_dtypes(include=['int64', 'float64']).columns 
                            if col != 'Exam_Score' and col in filtered_data.columns]
            
            # Row 1: Correlation Analysis
            st.subheader("Factor Correlation with Exam Score")
            
            if numerical_cols:
                # Calculate correlations
                correlations = []
                for col in numerical_cols:
                    corr = filtered_data[col].corr(filtered_data['Exam_Score'])
                    correlations.append({'Factor': col, 'Correlation': corr})
                
                corr_df = pd.DataFrame(correlations)
                corr_df = corr_df.sort_values('Correlation', ascending=False)
                
                # Create a bar chart of correlations
                fig = px.bar(corr_df, x='Factor', y='Correlation',
                           color='Correlation',
                           color_continuous_scale=px.colors.diverging.RdBu,
                           range_color=[-1, 1],
                           title="Correlation of Factors with Exam Score")
                
                # Add a reference line at 0
                fig.add_shape(
                    type='line',
                    x0=-0.5,
                    x1=len(corr_df)-0.5,
                    y0=0,
                    y1=0,
                    line=dict(color='black', width=1, dash='dash')
                )
                
                fig.update_layout(xaxis_title="", yaxis_title="Correlation Coefficient")
                st.plotly_chart(fig, use_container_width=True)
                
                # Add interpretation
                st.markdown("""
                **Interpretation Guide:**
                - **Positive values (blue)**: As this factor increases, exam scores tend to increase
                - **Negative values (red)**: As this factor increases, exam scores tend to decrease
                - **Values close to 1 or -1** indicate stronger relationships
                - **Values close to 0** indicate weaker relationships
                """)
            
            # Row 2: Scatter Plot Analysis
            st.subheader("Detailed Factor Analysis")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if numerical_cols:
                    selected_factor = st.selectbox("Select a factor to analyze:", numerical_cols)
                    show_trendline = st.checkbox("Show Trend Line", value=False)
                    if not STATSMODELS_AVAILABLE and show_trendline:
                        st.warning("Trendline not available without statsmodels package")
                        show_trendline = False
                    
                    # Use boolean flag instead of string comparison to avoid issues
                    use_color = st.checkbox("Color by category", value=False)
                    
                    # Only show category selector if color is enabled
                    if use_color:
                        color_by = st.selectbox("Select category:", categorical_cols)
                    else:
                        color_by = None  # No coloring selected
            
            with col2:
                if numerical_cols:
                    # Create scatter plot with more reliable color handling
                    if use_color and color_by is not None:
                        # Only add color when explicitly enabled
                        fig = px.scatter(filtered_data, 
                                       x=selected_factor, 
                                       y="Exam_Score", 
                                       color=color_by,  # Now this will always be a valid column name
                                       trendline="ols" if show_trendline and STATSMODELS_AVAILABLE else None,
                                       title=f"Impact of {selected_factor.replace('_', ' ')} on Exam Score")
                    else:
                        # No color parameter when disabled
                        fig = px.scatter(filtered_data, 
                                       x=selected_factor, 
                                       y="Exam_Score",
                                       trendline="ols" if show_trendline and STATSMODELS_AVAILABLE else None,
                                       title=f"Impact of {selected_factor.replace('_', ' ')} on Exam Score")
                    
                    fig.update_layout(xaxis_title=selected_factor.replace('_', ' '), 
                                    yaxis_title="Exam Score")
                    st.plotly_chart(fig, use_container_width=True)
            
            # Row 3: Key Insights
            st.subheader("Key Insights")
            
            # Calculate top positive and negative factors
            if numerical_cols and len(corr_df) > 0:
                top_positive = corr_df[corr_df['Correlation'] > 0].head(3)
                top_negative = corr_df[corr_df['Correlation'] < 0].sort_values('Correlation').head(3)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Top Positive Factors:**")
                    for _, row in top_positive.iterrows():
                        st.markdown(f"- **{row['Factor'].replace('_', ' ')}** (Correlation: {row['Correlation']:.2f})")
                
                with col2:
                    st.markdown("**Top Negative Factors:**")
                    if not top_negative.empty:
                        for _, row in top_negative.iterrows():
                            st.markdown(f"- **{row['Factor'].replace('_', ' ')}** (Correlation: {row['Correlation']:.2f})")
                    else:
                        st.markdown("No significant negative correlations found.")
    
    # Tab 4: Relationship Explorer
    with tab4:
        st.header("Relationship Explorer")
        
        # Multi-factor analysis
        st.subheader("Multi-Factor Analysis")
        
        # Only proceed if we have numerical and categorical columns
        if len(numerical_cols) > 1 and len(categorical_cols) > 0:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                x_axis = st.selectbox("X-Axis (Numerical):", numerical_cols)
            with col2:
                y_axis = st.selectbox("Y-Axis (Numerical):", 
                                    [col for col in numerical_cols if col != x_axis])
            with col3:
                color_var = st.selectbox("Color By (Category):", categorical_cols)
            
            # Create scatter plot
            fig = px.scatter(filtered_data, x=x_axis, y=y_axis, 
                           color=color_var,
                           title=f"Relationship Between {x_axis.replace('_', ' ')} and {y_axis.replace('_', ' ')}")
            
            fig.update_layout(xaxis_title=x_axis.replace('_', ' '), 
                            yaxis_title=y_axis.replace('_', ' '))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough numerical or categorical variables for multi-factor analysis.")
        
        # Correlation Matrix
        st.subheader("Correlation Matrix")
        
        if len(numerical_cols) > 1:
            # Use all numerical columns
            corr_matrix = filtered_data[numerical_cols + ['Exam_Score']].corr()
            
            # Create heatmap
            fig = px.imshow(corr_matrix, 
                          text_auto='.2f',
                          color_continuous_scale=px.colors.diverging.RdBu_r,
                          title="Correlation Matrix of Numerical Factors",
                          zmin=-1, zmax=1)
            
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough numerical variables for correlation analysis.")
        
        # Insights from Relationships
        if show_details and len(numerical_cols) > 1:
            st.subheader("Insights from Variable Relationships")
            
            # Find pairs with strong correlations
            strong_correlations = []
            for i in range(len(numerical_cols)):
                for j in range(i+1, len(numerical_cols)):
                    col1, col2 = numerical_cols[i], numerical_cols[j]
                    corr = filtered_data[col1].corr(filtered_data[col2])
                    if abs(corr) >= 0.5:  # Only strong correlations
                        strong_correlations.append({
                            'Variable 1': col1.replace('_', ' '),
                            'Variable 2': col2.replace('_', ' '),
                            'Correlation': corr,
                            'Relationship': 'Positive' if corr > 0 else 'Negative'
                        })
            
            if strong_correlations:
                strong_corr_df = pd.DataFrame(strong_correlations)
                strong_corr_df = strong_corr_df.sort_values('Correlation', ascending=False)
                
                st.dataframe(strong_corr_df, use_container_width=True)
                
                st.markdown("""
                **What this means:**
                - **Strong positive correlations** suggest these factors often increase together
                - **Strong negative correlations** suggest as one factor increases, the other tends to decrease
                - These relationships may suggest underlying patterns in student behavior or circumstances
                """)
            else:
                st.info("No strong correlations found between numerical variables.")

else:
    # No data loaded
    st.warning("Please upload a data file or ensure S3 access to begin analysis.")
    
    # Show placeholder message
    st.info("Once data is loaded, you'll see a comprehensive analysis of student performance factors.")