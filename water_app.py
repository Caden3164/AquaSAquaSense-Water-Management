import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from openai import OpenAI

# Set Streamlit page config to wide layout
st.set_page_config(layout="wide")

# Initialize the OpenAI client using the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

st.markdown(
    """
    <style>
    /* Sidebar Styling */
    section[data-testid="stSidebar"] .css-1aumxhk {
        font-size: 24px !important;
    }
    section[data-testid="stSidebar"] h1 {
        font-size: 26px !important;
        color: #4CAF50;
    }
    section[data-testid="stSidebar"] .stRadio > label {
        font-size: 24px !important;
        color: #333;
    }
    section[data-testid="stSidebar"] .stRadio > div > label > div {
        font-size: 20px !important;
        color: #333;
    }

    /* Main Content Styling */
    .main .block-container {
        max-width: 90%;
        padding-top: 2rem;
    }

    /* Header Styling */
    h1.title {
        font-size: 36px;
        color: #4CAF50;
        text-align: center;
    }
    h2.header {
        font-size: 28px;
        color: #333;
    }

    /* Change the background color of the app */
    .main {
        background-color: #e6f7ff; /* Light blue color */
    }

    /* Optional: Change the sidebar background color */
    section[data-testid="stSidebar"] {
        background-color: #d9f2f8; /* Slightly different light blue */
    }

    /* Global Font Size */
    body {
        font-size: 18px; /* Increase the global font size */
    }

    /* Header Font Sizes */
    h1 {
        font-size: 50px; /* Title size */
    }
    h2 {
        font-size: 40px; /* Subheader size */
    }
    h3 {
        font-size: 35px; /* Smaller header size */
    }

    /* Text Elements */
    p, div, label {
        font-size: 20px; /* Increase size for paragraphs, divs, and labels */
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        font-size: 20px; /* Sidebar text size */
    }
    section[data-testid="stSidebar"] h1 {
        font-size: 30px; /* Sidebar title size */
    }
    section[data-testid="stSidebar"] .stRadio > label {
        font-size: 24px; /* Sidebar radio buttons */
    }
    section[data-testid="stSidebar"] .stRadio > div > label > div {
        font-size: 22px; /* Sub-label size */
    }

    /* Buttons */
    button {
        font-size: 22px !important; /* Increase button text size */
    }

    /* Graph Title and Axis Labels */
    .matplotlib-title {
        font-size: 30px; /* Larger graph title */
    }
    .matplotlib-axis-label {
        font-size: 22px; /* Larger axis labels */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Define the get_completion function
def get_completion(prompt, model="gpt-3.5-turbo"):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an environmental specialist. Provide concise, personalized water-saving advice based on the user's input and data."},
            {"role": "user", "content": prompt},
        ]
    )
    return completion.choices[0].message.content


# Function to analyze faucet data and generate summary/graph
def analyze_faucet_data(file_path="faucet_usage_data.csv"):
    try:
        
        st.subheader("Faucet Water Usage Analysis")
        st.markdown(
            """
            Welcome to the Faucet Data Analyzer! Using data collected from your **AquaSense Smart Faucet**, 
            we provide a detailed breakdown of your water usage across different faucets and devices.
            The smart faucet tracks water flow and usage in real-time, enabling us to identify significant patterns 
            or anomalies, such as overuse in certain areas. This analysis will help you make more informed decisions 
            to conserve water and save money. Scroll down to view the visualizations and insights below.
            """
        )
        
        
        # Load and process data
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour

        # Aggregate data
        total_usage = df.groupby("faucet_id")["usage_liters"].sum()
        hourly_usage = df.groupby("hour")["usage_liters"].sum()

        # Identify discrepancies in faucet usage
        max_faucet = total_usage.idxmax()
        max_faucet_usage = total_usage.max()
        avg_faucet_usage = total_usage.mean()

        # Convert 24-hour clock to 12-hour clock with AM/PM
        hourly_usage.index = hourly_usage.index.map(
            lambda x: f"{x % 12 or 12} {'AM' if x < 12 else 'PM'}"
        )

        # Pie chart for total water usage by faucet
        st.subheader("Water Usage by Faucet")
        simplified_labels = {
            "Bathroom_1": "Bathroom Sink 1",
            "Bathroom_2": "Bathroom Sink 2",
            "Kitchen": "Kitchen Sink",
            "Shower_1": "Shower 1",
            "Shower_2": "Shower 2",
            "Dishwasher": "Dishwasher",
            "Garden_Hose": "Garden Hose"
        }
        colors = ["#76c7c0", "#ffdd88", "#6fa8dc", "#ff6961", "#77dd77", "#ffb347", "#84b6f4"]
        fig_pie, ax_pie = plt.subplots(figsize=(7, 7))
        ax_pie.pie(
            total_usage,
            labels=[simplified_labels[faucet] for faucet in total_usage.index],
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 12, 'fontname': 'Arial'},
            colors=colors
        )
        ax_pie.set_title("Water Usage by Faucet", fontsize=16, fontname="Arial", color="#003fc3")
        ax_pie.axis('equal')  # Ensures pie chart is circular
        st.pyplot(fig_pie)

        # Line chart for hourly water usage trend
        st.subheader("Hourly Water Usage Trend")
        fig_line, ax_line = plt.subplots(figsize=(8, 5))
        hourly_usage.plot(kind="line", ax=ax_line, marker='o', color='blue', linewidth=2)
        ax_line.set_title("Hourly Water Usage Trend", fontsize=14)
        ax_line.set_xlabel("Time of Day (12-hour clock)", fontsize=12)
        ax_line.set_ylabel("Water Usage (liters)", fontsize=12)
        ax_line.grid(axis='y', linestyle='--', alpha=0.7)
        y_max = hourly_usage.max()
        ax_line.set_ylim(0, y_max * 1.2)  # Add a 20% margin above the highest value
        st.pyplot(fig_line)

        # Dynamically generate advice using the OpenAI API
        peak_hour = hourly_usage.idxmax()
        total_usage_liters = total_usage.sum()
        peak_usage = hourly_usage.max()  # Peak water usage in liters

        # Add this updated prompt logic in the relevant section of your code
        prompt = f"""
        Based on the user's water usage data:
        - Total water usage: {total_usage_liters:.2f} liters.
        - The faucet or machine with the highest water usage is '{max_faucet}', using {max_faucet_usage:.0f} liters.
        - The peak water usage hour is {peak_hour}, with around {peak_usage:.0f} liters used.

        Please provide actionable advice addressing all water usage areas. Highlight the overuse of '{max_faucet}' but also provide suggestions for improving efficiency across all faucets. The response should be holistic, covering potential overuse, general conservation tips, and addressing peak usage patterns. Avoid overly focusing on a single faucet. Write the advice as a short, conversational paragraph.
        """

        advice = get_completion(prompt)

        # Display the dynamically generated advice
        st.markdown("### AI-Generated Water-Saving Advice")
        st.write(advice)

        # Text box for user questions
        st.markdown("### Ask a Question")
        user_question = st.text_input(
            "Have any questions or need further clarification? Type your question below:"
        )
        if st.button("Get Answer"):
            if user_question.strip():
                # Generate a response from the API
                question_prompt = f"""
                The user asked the following question based on their water usage data: {user_question}.
                Please provide a clear and concise response to address their query. Avoid technical jargon and explain in simple terms.
                """
                answer = get_completion(question_prompt)
                st.success("AI's Response:")
                st.write(answer)
            else:
                st.warning("Please enter a question before submitting.")

    except FileNotFoundError:
        st.error("File not found. Please ensure the file exists and try again.")
    except Exception as e:
        st.error(f"An error occurred: {e}")



# Residential questionnaire
def residential_questionnaire():
    st.subheader("Residential Water Usage Questionnaire")
    household_size = st.selectbox("Household size:", ["1", "2", "3", "4", "5+"])
    activities = st.selectbox("Water-intensive activities (including washing laundry, running the dishwasher, washing cars at home etc.) frequency:", ["Daily", "Several times a week", "Weekly", "Rarely"])
    practices = st.multiselect("Water-saving practices:", ["Low-flow showerheads", "Faucet aerators", "Reusing water", "Reducing shower time", "None"])
    motivation = st.selectbox("Primary motivation for saving water:", ["Environmental concern", "Reducing bills", "Water scarcity", "Other"])

    # Generate a prompt with motivations explicitly included
    prompt = f"""
    User Details:
    - Household Size: {household_size}
    - Water-Intensive Activities: {activities}
    - Water-Saving Practices: {', '.join(practices)}
    - Motivation: {motivation}
    
    Provide concise, actionable advice tailored to their motivation and water usage. After providing advice, also provide some simple statistics to support how much water or money that making these changes could save the user. Provide actual dollar amounts that might be saved on the water bill each month of year. Remember that the user might not be technical or intelligent, so keep it clear and simple. Include the statistics together with the water saving advice instead of in its own section. Concisely elaborate on the statistics to explain to the user what the statistics mean, because the everyday user might not understand gallons or litres.
    """
    if st.button("Get Advice"):
        advice = get_completion(prompt)
        
        # Clean and sanitize the AI response
        cleaned_advice = advice.replace("_", "").replace("*", "").strip()
        
        # Display the advice
        st.markdown("### AI-Generated Water-Saving Advice")
        st.markdown(cleaned_advice, unsafe_allow_html=False)

# Farmer's water usage questionnaire
def farmers_questionnaire():
    st.subheader("Farmer's Water Usage and Irrigation Advice")

    # Farmer inputs
    crop_type = st.selectbox("Type of crop:", ["Wheat", "Corn", "Rice", "Soybeans", "Other"])
    irrigation_method = st.selectbox("Irrigation method:", ["Drip", "Sprinkler", "Flood", "Furrow", "Other"])
    soil_type = st.selectbox("Soil type:", ["Clay", "Sandy", "Loamy", "Silty", "Peaty", "Other"])
    land_size = st.number_input("Enter the size of your land (in acres):", min_value=0.0, step=0.1)
    water_source = st.selectbox("Primary water source:", ["Well", "River", "Rainwater Harvesting", "Municipal Supply", "Other"])

    # Optional fields
    additional_notes = st.text_area("Additional notes or concerns (optional):")

    # Contextual advice prompt
    prompt = f"""
    The farmer has provided the following details:
    - Crop Type: {crop_type}
    - Irrigation Method: {irrigation_method}
    - Soil Type: {soil_type}
    - Land Size: {land_size:.1f} acres
    - Primary Water Source: {water_source}
    - Additional Notes: {additional_notes if additional_notes else 'None'}
    - Average Rainfall in San Jose, California: 15.82 inches annually

    Remember that the user themselves is the farmer So the response should be addressed to the user themselves.

    Based on these details, provide advice on the following:
    1. Optimal water usage and irrigation practices tailored to their crop type, soil type, and irrigation method.
    2. Expected water requirements for the specified land size.
    3. Suggestions to conserve water based on their water source and other provided details.
    Ensure that the advice is simple and actionable for a non-technical farmer.
    """

    # Button to get advice
    if st.button("Get Water Usage Advice for Farming"):
        advice = get_completion(prompt)
        st.success("Personalized Water-Saving Advice for Farmers")
        st.write(advice)



# Main app with improved session state handling
def main():

     # Enhanced CSS with global text color for main content
    st.markdown(
    f"""
    <style>
    /* Main content background and global text color */
    .main {{
        background-color: #e9f9fa; /* Light blue background for main content */
        color: #05176c; /* Darker blue text for contrast */
    }}

    /* Apply a global text color for all content in the main container */
    .main .block-container {{
        color: #05176c; /* Ensures all text in main content is this color */
        max-width: 90%;
        padding: 2rem;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        border: 1px solid #76dfe9;
    }}

    /* Specific text styles */
    h1, h2, h3, h4, h5, h6 {{
        color: #003fc3; /* Dark blue for all headers */
    }}
    p, div {{
        color: #05176c; /* Primary dark text color for paragraphs and divs */
    }}

    /* Title styling */
    .title {{
        font-size: 3em;
        color: #003fc3; /* Dark blue for high emphasis */
        text-align: center;
        font-weight: bold;
        margin-bottom: 0.5em;
    }}

    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background-color: #CDD8D8;
        color: #05176c;
    }}

    /* Additional styling omitted for brevity */
    </style>
    """,
    unsafe_allow_html=True
)
    st.markdown("<h1 class='title'>Water Usage Application</h1>", unsafe_allow_html=True)

    # Initialize session state for navigation
    if "page" not in st.session_state:
        st.session_state.page = "Home"

    # Sidebar navigation
    st.sidebar.image(
    "https://raw.githubusercontent.com/Caden3164/Final/main/AquaSense_Logo.webp", 
    use_column_width=True)
    # Styled AquaSense title in the sidebar with Courier New
    st.sidebar.markdown(
    """
    <style>
    .aqua-sense-title {
        font-family: 'Courier New', monospace; /* Use Courier New as the font */
        font-size: 32px;
        color: #05176c; /* Use the specified color */
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    </style>
    <h1 class="aqua-sense-title">AquaSense</h1>
    """,
    unsafe_allow_html=True
)
    st.sidebar.title("Navigation")
    nav_options = ["Home", "Residential Advice", "Analyze Faucet Data", "Farmer's Water Usage"]
    selected_page = st.sidebar.radio("Choose a section", nav_options, index=nav_options.index(st.session_state.page))

    # Set session state based on sidebar selection
    if selected_page != st.session_state.page:
        st.session_state.page = selected_page

    # Home page functionality
    if st.session_state.page == "Home":
        st.markdown("### Welcome to the Water Usage Application!")
        st.markdown(
            "This app is designed to help you manage and conserve water effectively, "
            "whether you're using water at home or on a farm."
        )
        user_type = st.radio(
            "Please select your role:",
            ["Everyday Water User", "Agricultural Producer"]
        )
        if st.button("Submit"):
            if user_type == "Everyday Water User":
                st.session_state.page = "Residential Advice"
            elif user_type == "Agricultural Producer":
                st.session_state.page = "Farmer's Water Usage"

    # Residential section
    elif st.session_state.page == "Residential Advice":
        st.button("Back to Home", on_click=lambda: setattr(st.session_state, "page", "Home"))
        residential_questionnaire()

    # Faucet data analytics section
    elif st.session_state.page == "Analyze Faucet Data":
        st.button("Back to Home", on_click=lambda: setattr(st.session_state, "page", "Home"))
        analyze_faucet_data()

    # Farmer's section
    elif st.session_state.page == "Farmer's Water Usage":
        st.button("Back to Home", on_click=lambda: setattr(st.session_state, "page", "Home"))
        farmers_questionnaire()




if __name__ == "__main__":
    main()

