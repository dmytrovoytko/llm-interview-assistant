import streamlit as st
import time
import uuid

from app_rag import get_answer
from db import (
    save_conversation,
    save_feedback,
    get_recent_conversations,
    get_feedback_stats,
)


def print_log(message):
    print(message, flush=True)


def main():
    print_log("Starting the Interview Preparation Assistant application")
    st.set_page_config(
        page_title="Interview Assistant",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get help': 'https://github.com/dmytrovoytko/llm-interview-assistant',
            'Report a bug': "https://github.com/dmytrovoytko/llm-interview-assistant/issues",
            'About': "## Let's get perfectly prepared for a job interview!"
        }
    )
    st.title("✨ Interview Preparation Assistant")

    # Session state initialization
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
        print_log(
            f"New conversation started with ID: {st.session_state.conversation_id}"
        )
    if "count" not in st.session_state:
        st.session_state.count = 0
        print_log("Feedback count initialized to 0")

    positions = {"data engineer": "de", "machine learning engineer": "mle"}
    # Position selection
    position_choice = st.selectbox(
        "Select a position:",
        positions.keys(),
    )
    print_log(f"User selected position: {position_choice}")

    # put options horizontally
    col1, col2, col3 = st.columns(3)
    # Model selection
    model_choice = col1.selectbox(
        "Select a model:",
        ["ollama/phi3.5", "ollama/phi3", "openai/gpt-3.5-turbo", "openai/gpt-4o", "openai/gpt-4o-mini"],
    )
    print_log(f"User selected model: {model_choice}")

    # Search type selection
    search_type = col2.radio("Select search type:", ["Text", "Vector"], horizontal=True)
    print_log(f"User selected search type: {search_type}")

    # Response length selection
    response_length = col3.radio("Select response length:", ["S", "M", "L"], horizontal=True)
    print_log(f"User selected response length: {response_length}")

    # User input
    user_input = st.text_input("Enter your question:", 'What is Data Engineering?')

    if st.button("🪄 Find the answer"):
        print_log(f"User asked: '{user_input}'")
        with st.spinner("Processing..."):
            # Generate a new conversation ID for next question
            st.session_state.conversation_id = str(uuid.uuid4())
            print_log(
                f"Getting answer from assistant using {model_choice} model and {search_type} search"
            )
            start_time = time.time()
            answer_data = get_answer(user_input, position_choice, model_choice, search_type, response_length)
            print_log(f"Answer received in {time.time() - start_time:.2f} seconds")
            st.success("Completed!")
            st.write(answer_data["answer"])

            # Display monitoring information
            st.write(f"Response time: {answer_data['response_time']:.2f} seconds")
            st.write(f"Relevance: {answer_data['relevance']}")
            st.write(f"Model used: {answer_data['model_used']}")
            st.write(f"Total tokens: {answer_data['total_tokens']}")
            if answer_data["openai_cost"] > 0:
                st.write(f"OpenAI cost: ${answer_data['openai_cost']:.4f}")

            # Save conversation to database
            print_log("Saving conversation to database")
            save_conversation(
                st.session_state.conversation_id, user_input, answer_data, position_choice
            )
            print_log("Conversation saved successfully")

    # Feedback buttons
    # col1, col2 = st.columns(2)
    # with col1:
    #     if st.button(":+1:"):
    #         st.session_state.count += 1
    #         print_log(
    #             f"Positive feedback received. New count: {st.session_state.count}"
    #         )
    #         save_feedback(st.session_state.conversation_id, 1)
    #         print_log("Positive feedback saved to database")
    # with col2:
    #     if st.button(":-1:"):
    #         st.session_state.count -= 1
    #         print_log(
    #             f"Negative feedback received. New count: {st.session_state.count}"
    #         )
    #         save_feedback(st.session_state.conversation_id, -1)
    #         print_log("Negative feedback saved to database")

    sentiment_mapping = [-2, -1, 0, 1, 2]
    selected = st.feedback("stars") # "faces"
    if selected is not None:
        feedback_value = sentiment_mapping[selected]
        st.session_state.count += feedback_value
        sentiment = 'Positive' if feedback_value>0 else 'Negative'
        print_log(
            f"{sentiment} feedback received. New count: {st.session_state.count}"
        )
        save_feedback(st.session_state.conversation_id, feedback_value)
        print_log(f"{sentiment} feedback saved to database")

    st.write(f"Current feedback balance: {st.session_state.count}")

    # Display recent conversations
    st.subheader("Recent Conversations")
    relevance_filter = st.selectbox(
        "Filter by relevance:", ["All", "RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"]
    )
    recent_conversations = get_recent_conversations(
        limit=5, relevance=relevance_filter if relevance_filter != "All" else None
    )
    for conv in recent_conversations:
        st.write(f"Q: {conv['question']}")
        st.write(f"A: {conv['answer']}")
        st.write(f"Relevance: {conv['relevance']}")
        st.write(f"Model: {conv['model_used']}")
        st.write("---")

    # Display feedback stats
    feedback_stats = get_feedback_stats()
    st.subheader("Overall feedback Statistics")
    st.write(f"Positive: {feedback_stats['thumbs_up']}, Negative: {feedback_stats['thumbs_down']}")


print_log("Streamlit app loop completed")


if __name__ == "__main__":
    print_log("Interview Preparation Assistant application started")
    main()
