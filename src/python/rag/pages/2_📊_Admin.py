import os
import tempfile

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from grongier.pex import Director

# Director setup for chat service
st.session_state.chat_service = Director.create_python_business_service("ChatService")

st.set_page_config(
    page_title="ChatIRIS - Admin",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

categories = {
    "incentive": {
        "keys": [
            "increase_cure",
            "increase_lifespan",
            "gain_reassurance",
            "gain_control",
        ],
        "description": "the user's motivating factors and perceived benefits associated with cancer screening."
    },
    "vulnerability": {
        "keys": [
            "family_medical_history",
            "own_medical_history",
            "risk_factor_exposure",
            "observed_symptoms",
        ],
        "description": "the user's perception of their susceptibility to developing colorectal cancer."
    },
    "barriers": {
        "keys": [
            "financial_concerns",
            "discomfort_and_side_effects",
            "time_constraints",
            "social_embarrassment",
            "tendency_to_deny",
            "difficult_preparation",
        ],
        "description": "how convenient cancer screening is for the user, based on their perceived obstacles and challenges."
    }
}
category_types = list(categories.keys())

def init_session():
    #* Load score agent's scores
    if "scores" not in st.session_state:
        scores = st.session_state.chat_service.retrieve_scores()
        st.session_state["scores"] = scores

        # Initialize scores
        category_scores = {category: {key: [] for key in details["keys"]} for category, details in categories.items()}

        # Extract the scores
        for round in scores:
            for category, details in categories.items():
                for key in details["keys"]:
                    category_scores[category][key].append(round[key])
        st.session_state["category_scores"] = category_scores

    #* Load score agent's beliefs
    if "beliefs" not in st.session_state:
        st.session_state["beliefs"] = st.session_state.chat_service.retrieve_beliefs()

# Define plot_scores function using Plotly
def plot_scores(scores, labels):
    # Create a Plotly figure
    fig = go.Figure()

    for i, series in enumerate(scores):
        fig.add_trace(
            go.Scatter(
                x=list(range(len(series))),
                y=series,
                mode="lines",
                name=f"{labels[i]}",
                line=dict(shape="spline"),
            )
        )

    # Update layout
    fig.update_layout(
        xaxis_title="Dialogue Round",
        yaxis_title="Score Value",
        template="plotly_white",
        legend=dict(yanchor="top", y=-0.2, xanchor="right", x=0.99),
        margin=dict(t=0, b=50),
    )

    return fig

def display_scores():
    data = st.session_state["scores"]
    placeholder = st.empty()

    category_scores = {category: [] for category in categories.keys()}

    for round in data:
        for category, details in categories.items():
            scores = [round[key] for key in details["keys"]]
            category_scores[category].append(np.average(scores))

    fig = plot_scores(
        [category_scores[category] for category in category_types],
        labels=[category.capitalize() for category in category_types],
    )
    placeholder.plotly_chart(fig, use_container_width=True)

    for category, details in categories.items():
        with st.expander(f"{category.capitalize()} Scores"):
            st.info(f"{category.capitalize()} measures {details['description']}")

            individual_scores = {key: [] for key in details["keys"]}
            for round in data:
                for key in details["keys"]:
                    individual_scores[key].append(round[key])

            fig = plot_scores(
                [individual_scores[key] for key in details["keys"]],
                labels=[st.session_state["beliefs"][key] for key in details["keys"]],
            )
            st.plotly_chart(fig, use_container_width=True)

def main():
    init_session()
    st.title("📊 ChatIRIS - Health Belief Monitoring")

    display_scores()

if __name__ == "__main__":
    main()
