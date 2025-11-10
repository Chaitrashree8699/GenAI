import streamlit as st
import os
from dotenv import load_dotenv
from agents import ResearchAgents
from data_loader import DataLoader

load_dotenv()

print("ok")

# Streamlit UI Title
st.title("Virtual Literature Review Generator")

# Retrieve the API key from environment variables
groq_api_key = os.getenv("GROQ_API_KEY")

# Check if API key is set, else stop execution
if not groq_api_key:
    st.error("GROQ_API_KEY is missing. Please set it in your environment variables.")
    st.stop()

# Initialize AI Agents for literature review and analysis
agents = ResearchAgents(groq_api_key)

# Initialize DataLoader for fetching research papers
data_loader = DataLoader()

# Input field for the user to enter a research topic
query = st.text_input("Enter a research topic:")

# Variable to store all summaries of paper
if "all_summaries" not in st.session_state:
    st.session_state.all_summaries = []

if "literature_review" not in st.session_state:
    st.session_state.literature_review = ""

# When the user clicks "Search"
if st.button("Search"):
    with st.spinner("Fetching research papers..."):  # Show a loading spinner
        
        # Fetch research papers from ArXiv
        arxiv_papers = data_loader.fetch_arxiv_papers(query)
        all_papers = arxiv_papers

        # If no papers are found, display an error message
        if not all_papers:
            st.error("Failed to fetch papers. Try again!")
        else:
            processed_papers = []

            # Process each paper: generate small summary
            for paper in all_papers:
                # Fetching the paper summary using user_proxy_agent
                summary_response = agents.user_proxy_agent.initiate_chat(agents.summarizer_agent, message=f"Summarize the following paper: {paper['summary']}", max_turns=1)
                # Accessing the 'content' attribute from the summary_response directly
                if hasattr(summary_response, 'content') and summary_response.content:
                    summary = summary_response.content
                summary = agents.summarize_paper(paper['summary'])  # Generate summary

                # Append each summary to the all_summaries variable
                st.session_state.all_summaries.append(summary)

                processed_papers.append({
                    "title": paper["title"],
                    "link": paper["link"],
                    "summary": summary,
                })

            # Display the processed research papers
            st.write("Top 6 Research Papers based on topic given:")
            for i, paper in enumerate(processed_papers, 1):
                st.write(f"### {i}. {paper['title']}")  # Paper title
                st.write(f"[Read Paper]({paper['link']})")  # Paper link

#code to fetch literature review
if st.button("Fetch Literature Review"):
    combined_summaries = "\n\n".join(st.session_state.all_summaries)
    literature_review_response = agents.user_proxy_agent.initiate_chat(
            agents.literature_review_agent,
            message=f"Generate a literature review using these research summaries:\n\n{combined_summaries}",
            max_turns=1
        )
    if combined_summaries:
        st.session_state.literature_review = agents.literature_review(combined_summaries)
        st.subheader("Literature Review of Paper:")
        st.write(st.session_state.literature_review)

# Get the feedback from user and refine the literature review
st.subheader("Refine the Literature Review Based on Your Feedback:")
feedback = st.text_area("Provide feedback for improvements (optional):")

  # Initialize storage for literature review
if "feedback_history" not in st.session_state:
    st.session_state.feedback_history = []

if st.button("Refine Lierature review"):
    if feedback.strip():  # If user provides feedback
        combined_summaries = "\n\n".join(st.session_state.all_summaries)
        st.session_state.literature_review = agents.literature_review(combined_summaries)
        literature_review=agents.literature_review(combined_summaries)
        st.session_state.feedback_history.append(feedback)  

        # Combine past and new feedback
        all_feedback = "\n".join(st.session_state.feedback_history)

        # Refine the literature review based on all feedback
        refined_literature_review_response = agents.user_proxy_agent.initiate_chat(
            agents.feedback_agent, 
            message=f"Refine the following literature review based on user feedback.\n\n"
                    f"Previous Literature Review: {st.session_state.literature_review}\n\n"
                    f"All User Feedback Given:\n{all_feedback}\n\n"
                    f"Provide a revised summary incorporating all feedback.",
            max_turns=2
        )

        # Get the updated literature review
        refined_summary = agents.refine_literature_review_with_feedback(literature_review, all_feedback)  

        st.write(f"**Refined Summary:** {refined_summary}")
    else:
        st.warning("No feedback provided. Summary remains the same.")
