"""
Production Web Push Notification Service for CareerCompass.
Implements RFC 8291 / RFC 8292 standard Web Push using VAPID keys.
Features:
- Automatic persistent VAPID key generation and loading.
- Safe public key extraction for browser pushManager.subscribe.
- Multi-device delivery per user.
- Automatic removal of expired (HTTP 404/410) subscriptions.
- Offline and local testing resilience.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from py_vapid import Vapid, b64urlencode
from pywebpush import webpush, WebPushException
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from db_repository import PushRepository

logger = logging.getLogger("careercompass.push")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
VAPID_FILE = os.path.join(DATA_DIR, "vapid_keys.json")


class PushService:
    _vapid_instance: Optional[Vapid] = None
    _public_key_b64: Optional[str] = None
    _private_pem_str: Optional[str] = None

    @classmethod
    def _init_vapid(cls) -> None:
        if cls._vapid_instance:
            return

        os.makedirs(DATA_DIR, exist_ok=True)

        # 1. Check environment variables
        env_pub = os.environ.get("VAPID_PUBLIC_KEY", "").strip()
        env_priv = os.environ.get("VAPID_PRIVATE_KEY", "").strip()

        if env_pub and env_priv:
            try:
                v = Vapid.from_pem(env_priv.encode("utf-8"))
                cls._vapid_instance = v
                cls._private_pem_str = env_priv
                raw_pub = v.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
                cls._public_key_b64 = b64urlencode(raw_pub)
                logger.info("Loaded VAPID keys from environment variables.")
                return
            except Exception as e:
                logger.warning(f"Could not load VAPID keys from env: {e}")

        # 2. Check local file
        if os.path.exists(VAPID_FILE):
            try:
                with open(VAPID_FILE, "r", encoding="utf-8") as f:
                    keys = json.load(f)
                priv_pem = keys.get("private_key")
                v = Vapid.from_pem(priv_pem.encode("utf-8"))
                cls._vapid_instance = v
                cls._private_pem_str = priv_pem
                raw_pub = v.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
                cls._public_key_b64 = b64urlencode(raw_pub)
                return
            except Exception as e:
                logger.warning(f"Could not load local VAPID file: {e}")

        # 3. Generate new persistent VAPID keys
        v = Vapid()
        v.generate_keys()
        priv_pem = v.private_pem().decode("utf-8")
        raw_pub = v.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
        pub_b64 = b64urlencode(raw_pub)

        keys_data = {
            "private_key": priv_pem,
            "public_key": pub_b64,
            "created_at": "now"
        }
        try:
            with open(VAPID_FILE, "w", encoding="utf-8") as f:
                json.dump(keys_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not persist VAPID keys: {e}")

        cls._vapid_instance = v
        cls._private_pem_str = priv_pem
        cls._public_key_b64 = pub_b64
        logger.info("Generated and saved new persistent VAPID key pair.")

    @classmethod
    def get_public_key(cls) -> str:
        """Returns the Base64 URL-safe uncompressed public key for applicationServerKey."""
        cls._init_vapid()
        return cls._public_key_b64 or ""

    @classmethod
    def send_push_notification(cls, subscription_info: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches an encrypted Web Push message to a single device.
        """
        cls._init_vapid()
        claims_email = os.environ.get("VAPID_CLAIMS_EMAIL", "admin@careercompass.gov.in")
        claims = {"sub": f"mailto:{claims_email}"}

        json_data = json.dumps(payload)
        endpoint = subscription_info.get("endpoint", "")

        try:
            response = webpush(
                subscription_info=subscription_info,
                data=json_data,
                vapid_private_key=cls._private_pem_str,
                vapid_claims=claims,
                ttl=86400  # 24 hours
            )
            return {"status": "success", "endpoint": endpoint, "code": getattr(response, "status_code", 201)}
        except WebPushException as ex:
            logger.warning(f"WebPush delivery error for {endpoint}: {ex}")
            # If subscription has expired or is unsubscribed on device
            if ex.response and ex.response.status_code in (404, 410):
                logger.info(f"Deactivating expired push subscription: {endpoint}")
                PushRepository.deactivate_subscription(endpoint)
            return {"status": "error", "endpoint": endpoint, "error": str(ex)}
        except Exception as e:
            logger.error(f"Unexpected push delivery failure: {e}")
            return {"status": "error", "endpoint": endpoint, "error": str(e)}

    @classmethod
    def send_push_to_user(cls, user_id: int, title: str, message: str, deep_link: str = "/", tag: str = "general") -> List[Dict[str, Any]]:
        """
        Dispatches web push alerts to all active devices registered by this user.
        """
        subscriptions = PushRepository.get_subscriptions_for_user(user_id)
        if not subscriptions:
            return []

        payload = {
            "title": title,
            "body": message,
            "icon": "/static/img/icon-192.png",
            "badge": "/static/img/icon-192.png",
            "tag": tag,
            "data": {
                "url": deep_link
            }
        }

        results = []
        for sub in subscriptions:
            sub_info = {
                "endpoint": sub["endpoint"],
                "keys": {
                    "p256dh": sub["p256dh_key"],
                    "auth": sub["auth_key"]
                }
            }
            res = cls.send_push_notification(sub_info, payload)
            results.append(res)
        return results
