import os
import sys
from dotenv import load_dotenv

_backend_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_backend_dir, "..", ".env"))

os.environ["AGENT_MANIFEST_FILE"] = os.path.join(_backend_dir, "registries", "manifest.hocon")
os.environ["AGENT_TOOL_PATH"] = os.path.join(_backend_dir, "coded_tools")

_existing_pythonpath = os.environ.get("PYTHONPATH", "")
if _backend_dir not in _existing_pythonpath.split(os.pathsep):
    os.environ["PYTHONPATH"] = (
        f"{_backend_dir}{os.pathsep}{_existing_pythonpath}" if _existing_pythonpath else _backend_dir
    )
sys.path.insert(0, _backend_dir)

from neuro_san.client.agent_session_factory import DirectAgentSessionFactory


def invoke_agent(agent_name: str, user_text: str, sly_data=None, chat_context=None):
    """Invoke a neuro-san agent and return its response."""
    factory = DirectAgentSessionFactory()
    session = factory.create_session(agent_name=agent_name, use_direct=True, metadata={})

    request_payload = {"user_message": {"text": user_text}, "sly_data": sly_data}
    if chat_context:
        request_payload["chat_context"] = chat_context

    stream = session.streaming_chat(request_payload)
    msg = []
    for chat_msg in stream:
        msg.append(chat_msg)
        if chat_msg.get("done") is True:
            break

    return msg[-1] if msg else {}


if __name__ == "__main__":
    test_input = "spent 3 hours debugging login timeout on prod, redis session TTL was 5 seconds instead of 5 minutes, fixed it"
    response = invoke_agent("jira_ticket", test_input)
    print(response.get("response", {}).get("text", str(response)))
