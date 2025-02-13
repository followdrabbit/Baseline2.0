import time
from openai import OpenAI
import streamlit as st

class OpenAIService:
    """Handles interaction with the OpenAI API."""

    @staticmethod
    def setup_client(api_key: str = None) -> OpenAI:
        """
        Initializes the OpenAI client with the provided API key or retrieves it from Streamlit secrets.
        """
        if not api_key:
            api_key = st.secrets.get("OpenAI_key")
            if not api_key:
                raise ValueError("API key is required to initialize OpenAI client.")
        return OpenAI(api_key=api_key)

    @staticmethod
    def process_file_content(file_content: str, assistant_id: str):
        """
        Sends the file content to the OpenAI assistant and retrieves the response.

        Args:
            file_content (str): Content of the file to be sent.
            assistant_id (str): ID of the configured assistant.

        Returns:
            str: Response generated by the assistant.
        """
        client = OpenAIService.setup_client()

        # Create a thread and send the file content
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(thread.id, role="user", content=file_content)
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)

        # Wait for the response
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id).status
            if run_status == "completed":
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                responses = [msg.content[0].text.value for msg in messages if msg.role == "assistant"]
                return "\n".join(responses)
            elif run_status in ["queued", "in_progress"]:
                time.sleep(3)
            else:
                raise RuntimeError(f"Unexpected run status: {run_status}")
