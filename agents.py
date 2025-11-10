import os
from autogen import AssistantAgent, UserProxyAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ResearchAgents:
    def __init__(self, api_key, max_turns=3):
        self.groq_api_key = api_key
        self.llm_config = {'config_list': [{'model': 'llama-3.3-70b-versatile', 'api_key': self.groq_api_key, 'api_type': "groq"}]}


        self.feedback_history = []

        # UserProxyAgent - Orchestrates interactions between agents
        self.user_proxy_agent = UserProxyAgent(
            name="user_proxy_agent",
            system_message="You are the controller that helps coordinate different agents for research assistance.",
            llm_config=self.llm_config,
            human_input_mode="ALWAYS",  
            code_execution_config=False
        )

        # Summarizer Agent - Summarizes research papers
        self.summarizer_agent = AssistantAgent(
            name="summarizer_agent",
            system_message="Summarize the retrieved research papers and present concise summaries to the user with atlease 200 words, JUST GIVE THE RELEVANT SUMMARIES OF THE RESEARCH PAPER AND NOT YOUR THOUGHT PROCESS.",
            llm_config=self.llm_config,
            human_input_mode="NEVER",
            code_execution_config=False
        )


        #Literature review Agent- Generate literature review
        self.literature_review_agent = AssistantAgent(
            name="literature_review_agent",
            system_message="Generate a structured literature review using the summaries of multiple research papers. Provide an overview of the research trends, findings, gaps, and future directions. ONLY PROVIDE THE REVIEW WITHOUT EXPLANATION OF YOUR THOUGHT PROCESS.",
            llm_config=self.llm_config,
            human_input_mode="NEVER",
            code_execution_config=False
        )


        # Feedback Agent - Get feedback from the user to refine the literature review
        self.feedback_agent = AssistantAgent(
            name="feedback_agent",
            system_message="Ask the user whether the summary looks good or if they want to suggest improvements.",
            llm_config=self.llm_config,
            human_input_mode="NEVER",
            code_execution_config=False
        )

    def summarize_paper(self, paper_summary):
        """Generates a summary of the research paper."""
        summary_response = self.summarizer_agent.generate_reply(
            messages=[{"role": "user", "content": f"Summarize this paper: {paper_summary}"}])
        return summary_response.get("content", "Summarization failed!") if isinstance(summary_response, dict) else str(summary_response)


    def literature_review(self, all_summaries):
        """Generates a structured literature review from multiple research paper summaries."""
        if not all_summaries.strip():
            return "No summaries provided for literature review."
        literature_review_response = self.literature_review_agent.generate_reply(
        messages=[{"role": "user", "content": f"Generate a literature review using these research summaries:\n\n{all_summaries}"}])
        return literature_review_response.get("content", "Literature review generation failed!") if isinstance(literature_review_response, dict) else str(literature_review_response)

    def refine_literature_review_with_feedback(self, literature_review, new_feedback):
        """Refines the literature review based on the feedback provided by the user."""
        refined_message = (f"Here is the original summary of a research paper:\n\n"f"{literature_review}\n\n"f"The user has provided the following feedback:\n{new_feedback}\n\n"f"Please refine the summary to incorporate the feedback while maintaining clarity and accuracy.")
        refined_summary_response = self.feedback_agent.generate_reply(messages=[{"role": "user", "content": refined_message}])
        return refined_summary_response.get("content", "Refinement failed!") if isinstance(refined_summary_response, dict) else str(refined_summary_response)

    