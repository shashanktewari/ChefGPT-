import streamlit as st
import requests
import json

# ------------------------------------------------------
# CONFIGURE THESE
# ------------------------------------------------------

LANGFLOW_BASE_URL = "http://localhost:7860"   # e.g https://api.langflow.com
FLOW_ID = "02b96436-d76f-432f-a2e7-632beb1c2bcf"
API_KEY = "sk-M1B07tZdSgNPTZE-B_CH14WH6FUce3K-6wHqk38Np1Q"    # required for cloud

# ------------------------------------------------------
# Streamlit UI
# ------------------------------------------------------

st.set_page_config(page_title="Recipe Finder", page_icon="🍲", layout="centered")

st.title("🍲 CheftGPT+")
st.write("Enter ingredients or describe what you're craving.")

ingredients = st.text_input("Ingredients / your request")
allergies = st.text_input("Allergies (optional)")
cuisine = st.text_input("Cuisine (optional)")

if st.button("Find Recipes"):
    if not ingredients:
        st.warning("Please enter some ingredients or a request.")
    else:
        with st.spinner("Talking to LangFlow..."):

            # ------------------------------------------------------
            # Build input_value EXACTLY how LangFlow expects
            # ------------------------------------------------------

            prompt = f"""
Ingredients / Request: {ingredients}
Allergies: {allergies}
Cuisine: {cuisine}
"""

            payload = {
                "input_value": prompt,
                "output_type": "chat",
                "input_type": "chat",

                # You may customize tweaks if needed,
                # here we simply pass an empty tweaks object
                "tweaks": {}
            }

            url = f"{LANGFLOW_BASE_URL}/api/v1/run/{FLOW_ID}?stream=false"
            headers = {
                "Content-Type": "application/json",
                "x-api-key": API_KEY
            }

            response = requests.post(url, json=payload, headers=headers)

            if response.status_code != 200:
                st.error(f"Error {response.status_code}: {response.text}")
            else:
                data = response.json()

                # ------------------------------------------------------
                # Parse LangFlow Response
                # The result is usually inside data["outputs"]
                # ------------------------------------------------------

                def extract_text(obj):
                    if isinstance(obj, dict):
                        if "message" in obj:
                            return obj["message"]
                        for v in obj.values():
                            res = extract_text(v)
                            if res:
                                return res
                    if isinstance(obj, list):
                        for i in obj:
                            res = extract_text(i)
                            if res:
                                return res
                    return None

                final_text = extract_text(data)

                if not final_text:
                    st.warning("No readable output found.")
                else:
                    st.subheader("🍽️ Results")
                    st.write(final_text)
