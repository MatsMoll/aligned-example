import datetime

import pandas as pd
import shap
import streamlit as st
import asyncio
from matplotlib import pyplot as plt
from aligned import RedisConfig

from loan_example.model import CreditScoringModel

async def load_model() -> CreditScoringModel:
    model = await CreditScoringModel.load_from_paths(
        model_filename="loan_example/model.bin",
        encoder_filename="loan_example/encoder.bin",
        feature_store_path="feature-store.json"
    )

    if not model.is_model_trained():
        raise Exception("The credit scoring model has not been trained. Please run run.py.")

    return model.with_source(RedisConfig.localhost())



def get_loan_request():
    zipcode = st.sidebar.text_input("Zip code", "94109")
    date_of_birth = st.sidebar.date_input(
        "Date of birth", value=datetime.date(year=1986, day=19, month=3)
    )
    ssn_last_four = st.sidebar.text_input(
        "Last four digits of social security number", "3643"
    )
    dob_ssn = f"{date_of_birth.strftime('%Y%m%d')}_{str(ssn_last_four)}"
    age = st.sidebar.slider("Age", 0, 130, 25)
    income = st.sidebar.slider("Yearly Income", 0, 1000000, 120000)
    person_home_ownership = st.sidebar.selectbox(
        "Do you own or rent your home?", ("RENT", "MORTGAGE", "OWN")
    )

    employment = st.sidebar.slider(
        "How long have you been employed (months)?", 0, 120, 12
    )

    loan_intent = st.sidebar.selectbox(
        "Why do you want to apply for a loan?",
        (
            "PERSONAL",
            "VENTURE",
            "HOMEIMPROVEMENT",
            "EDUCATION",
            "MEDICAL",
            "DEBTCONSOLIDATION",
        ),
    )

    amount = st.sidebar.slider("Loan amount", 0, 100000, 10000)
    interest = st.sidebar.slider("Preferred interest rate", 1.0, 25.0, 12.0, step=0.1)
    return {
        "zipcode": [int(zipcode)],
        "dob_ssn": [dob_ssn],
        "loan_id": [None],
        "person_age": [age],
        "person_income": [income],
        "person_home_ownership": [person_home_ownership],
        "person_emp_length": [float(employment)],
        "loan_intent": [loan_intent],
        "loan_amount": [amount],
        "loan_int_rate": [interest],
        "event_timestamp": [datetime.datetime.now()]
    }



async def load_features(model: CreditScoringModel, entities):
    return await model.features_for(entities)

async def predict(model, data, features, entities):
    return await model.predict(entities, data[features])

async def main():
    st.set_page_config(layout="wide")

    st.header("Training dataset")
    model = await load_model()
    features = model.store.request().request_result.feature_columns

    @st.cache_resource()
    def datasets(features: list[str]):
        trainset = pd.read_parquet("data/training_dataset.parquet")
        X = trainset[features]

        explainer = shap.TreeExplainer(model.classifier)
        shap_values = explainer.shap_values(X)
        return shap_values, trainset, X

    shap_values, trainset, X = datasets(features)

    trainset[:5]


    # Application
    st.title("Loan Application")

    # Input Side Bar
    st.header("User input:")
    loan_request = get_loan_request()
    df = pd.DataFrame.from_dict(loan_request)
    df

    # Full feature vector
    st.header("Feature vector (user input + zipcode features + user features):")
    vector, features = await load_features(model, loan_request)
    ordered_vector = loan_request.copy()
    key_list = vector.keys()
    key_list = sorted(key_list)
    for vector_key in key_list:
        if vector_key not in ordered_vector:
            ordered_vector[vector_key] = vector[vector_key]
    df = pd.DataFrame.from_dict(ordered_vector)
    df

    # Results of prediction
    st.header("Application Status (model prediction):")
    results = await predict(model, vector, features, loan_request)
    result = results[0]


    if result == 0:
        st.success("Your loan has been approved!")
    elif result == 1:
        st.error("Your loan has been rejected!")


    # Feature importance
    st.header("Feature Importance")

    left, mid, right = st.columns(3)
    with left:
        plt.title("Feature importance based on SHAP values")
        shap.summary_plot(shap_values[1], X)
        st.set_option("deprecation.showPyplotGlobalUse", False)
        st.pyplot(bbox_inches="tight")
        st.write("---")

    with mid:
        plt.title("Feature importance based on SHAP values (Bar)")
        shap.summary_plot(shap_values, X, plot_type="bar")
        st.pyplot(bbox_inches="tight")

if __name__ == "__main__":
    asyncio.run(main())