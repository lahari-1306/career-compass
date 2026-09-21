"""
Base class and contract for official source connectors.
Provides safe HTTP fetching, timeout protection, and normalized output.
"""
import urllib.request
import urllib.error
import ssl
from typing import List, Dict, Any, Optional

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 CareerCompass/2.0"

class BaseSourceConnector:
    source_id: str = "base"
    source_name: str = "Base Official Source"
    organization: str = "Official Organization"
    category: str = "General"
    official_url: str = "https://gov.in"
    source_type: str = "html_portal"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def safe_get(self, url: str) -> tuple[int, Optional[str], Optional[str]]:
        """
        Executes a safe GET request with timeout and error containment.
        Returns: (status_code, text_content, error_message)
        """
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": DEFAULT_USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9"
            }
        )
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as response:
                status = response.status
                raw_bytes = response.read()
                try:
                    text = raw_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    text = raw_bytes.decode("latin-1", errors="replace")
                return status, text, None
        except urllib.error.HTTPError as e:
            return e.code, None, f"HTTP Error {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            return 0, None, f"Network/URL Error: {e.reason}"
        except Exception as e:
            return 0, None, f"Request Exception: {str(e)}"

    def fetch_latest(self) -> List[Dict[str, Any]]:
        """
        Subclasses must override this to return a list of extracted opportunity dictionaries.
        """
        raise NotImplementedError("Each source connector must implement fetch_latest()")
