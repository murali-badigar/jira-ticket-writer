import datetime
import logging
import os
from typing import Any, Dict, Union

from neuro_san.interfaces.coded_tool import CodedTool

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "output")


class SaveTicket(CodedTool):
    """Saves a formatted JIRA ticket as a Markdown file and returns confirmation."""

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        content = args.get("content", "")
        if not content:
            return "Error: No content provided to save."

        base_name = args.get("filename", f"TICKET_{datetime.datetime.now().strftime(\"%Y%m%d_%H%M%S\")}")
        base_name = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in base_name)
        file_path = os.path.join(OUTPUT_DIR, f"{base_name}.md")

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info("Saved ticket to %s", file_path)
        return {"path": file_path, "message": f"Ticket saved to {file_path}"}

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        return self.invoke(args, sly_data)
