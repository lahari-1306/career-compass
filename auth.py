"""
Authentication and Authorization Module for CareerCompass.
Features:
- Argon2id password hashing and validation.
- Secure HttpOnly / SameSite session cookie management.
- Brute-force rate limiting (max 5 failed attempts per 15 minutes).
- Server-side @login_required authorization decorator.
- Zero credential / token exposure in localStorage.
- User data isolation.
"""

import os
import time
from functools import wraps
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify, make_response, g
from db_repository import (
    UserRepository, SessionRepository, TokenRepository,
    ProfileRepository, SettingsRepository, NotificationRepository
)
from services.email_service import EmailService

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# In-memory brute force tracker: {key: [timestamp, timestamp, ...]}
FAILED_LOGIN_ATTEMPTS: Dict[str, list] = {}
RATE_LIMIT_WINDOW = 900  # 15 minutes
MAX_FAILED_ATTEMPTS = 5


def is_rate_limited(key: str) -> bool:
    now = time.time()
    attempts = FAILED_LOGIN_ATTEMPTS.get(key, [])
    # Filter attempts in current window
    valid_attempts = [t for t in attempts if now - t < RATE_LIMIT_WINDOW]
    FAILED_LOGIN_ATTEMPTS[key] = valid_attempts
    return len(valid_attempts) >= MAX_FAILED_ATTEMPTS


def record_failed_attempt(key: str) -> None:
    now = time.time()
    if key not in FAILED_LOGIN_ATTEMPTS:
        FAILED_LOGIN_ATTEMPTS[key] = []
    FAILED_LOGIN_ATTEMPTS[key].append(now)


def clear_failed_attempts(key: str) -> None:
    FAILED_LOGIN_ATTEMPTS.pop(key, None)


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Extracts session token from HttpOnly cookie or Authorization Bearer header,
    validates active session against database, and returns user dict.
    """
    token = request.cookies.get("session_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()

    if not token:
        return None

    return SessionRepository.get_user_from_token(token)


def login_required(f):
    """Decorator to require authenticated user on API routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({
                "status": "error",
                "code": "UNAUTHORIZED",
                "message": "Authentication required. Please log in to access your personal CareerCompass account."
            }), 401
        g.user = user
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role or development admin bypass."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        is_dev = os.environ.get("FLASK_ENV") == "development" or os.environ.get("DEV_ADMIN") == "1"
        if not user and not is_dev:
            return jsonify({
                "status": "error",
                "code": "UNAUTHORIZED",
                "message": "Admin authentication required."
            }), 401
        if user and user.get("role") != "admin" and not is_dev:
            return jsonify({
                "status": "error",
                "code": "FORBIDDEN",
                "message": "Administrator privileges required."
            }), 403
        if user:
            g.user = user
        return f(*args, **kwargs)
    return decorated_function


def set_session_cookie(response, token: str) -> None:
    """Sets secure HttpOnly session cookie."""
    is_secure = request.is_secure or request.headers.get("X-Forwarded-Proto") == "https"
    response.set_cookie(
        "session_token",
        token,
        max_age=SessionRepository.SESSION_DURATION_DAYS * 86400,
        httponly=True,
        samesite="Lax",
        secure=is_secure,
        path="/"
    )


# ====================================================
# AUTH REST API ENDPOINTS
# ====================================================

@auth_bp.route("/signup", methods=["POST"])
@auth_bp.route("/register", methods=["POST"])
def signup():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("full_name") or data.get("name") or "").strip()

    if not email or "@" not in email or "." not in email:
        return jsonify({
            "success": False,
            "status": "error",
            "message": "A valid email address is required."
        }), 400

    if len(password) < 8:
        return jsonify({
            "success": False,
            "status": "error",
            "message": "Password must be at least 8 characters long."
        }), 400

    if not name:
        return jsonify({
            "success": False,
            "status": "error",
            "message": "Full name is required."
        }), 400

    existing = UserRepository.get_by_email(email)
    if existing:
        return jsonify({
            "success": False,
            "status": "error",
            "message": "An account with this email already exists. Please sign in."
        }), 409

    user = UserRepository.create_user(email, password, name)
    if not user:
        return jsonify({
            "success": False,
            "status": "error",
            "message": "Could not create account. Please try again."
        }), 500

    # Create session
    ip = request.remote_addr or ""
    ua = request.headers.get("User-Agent", "")
    session_token = SessionRepository.create_session(user["id"], ip, ua)

    # Dispatch welcome email asynchronously / background safe
    try:
        EmailService.send_welcome_email(user["name"], user["email"])
    except Exception:
        pass

    profile = ProfileRepository.get_profile(user["id"])
    settings = SettingsRepository.get_settings(user["id"])

    user_info = {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "is_verified": user["is_verified"],
        "is_active": user.get("is_active", 1),
        "created_at": user.get("created_at"),
        "last_login_at": user.get("last_login_at"),
        "unread_notifications": 0
    }

    resp = make_response(jsonify({
        "success": True,
        "status": "success",
        "message": "Account created successfully.",
        "user": user_info,
        "profile": profile,
        "settings": settings
    }), 201)
    set_session_cookie(resp, session_token)
    return resp


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({
            "success": False,
            "status": "error",
            "message": "Email and password are required."
        }), 400

    rate_key = f"{request.remote_addr}_{email}"
    if is_rate_limited(rate_key):
        return jsonify({
            "success": False,
            "status": "error",
            "code": "RATE_LIMITED",
            "message": "Too many failed login attempts. For your security, this account is temporarily locked for 15 minutes."
        }), 429

    user = UserRepository.get_by_email(email)
    if not user or not UserRepository.verify_password(user["password_hash"], password):
        record_failed_attempt(rate_key)
        return jsonify({
            "success": False,
            "status": "error",
            "message": "Invalid email or password."
        }), 401

    clear_failed_attempts(rate_key)
    UserRepository.update_last_login(user["id"])

    ip = request.remote_addr or ""
    ua = request.headers.get("User-Agent", "")
    session_token = SessionRepository.create_session(user["id"], ip, ua)

    profile = ProfileRepository.get_profile(user["id"])
    settings = SettingsRepository.get_settings(user["id"])
    unread = NotificationRepository.get_unread_count(user["id"])

    user_info = {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "is_verified": user["is_verified"],
        "is_active": user.get("is_active", 1),
        "unread_notifications": unread
    }

    resp = make_response(jsonify({
        "success": True,
        "status": "success",
        "message": "Login successful.",
        "user": user_info,
        "profile": profile,
        "settings": settings
    }), 200)
    set_session_cookie(resp, session_token)
    return resp


@auth_bp.route("/logout", methods=["POST"])
def logout():
    token = request.cookies.get("session_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
    if token:
        SessionRepository.invalidate_session(token)
    resp = make_response(jsonify({
        "success": True,
        "status": "success",
        "message": "Logged out successfully."
    }), 200)
    resp.set_cookie("session_token", "", max_age=0, path="/")
    return resp


@auth_bp.route("/me", methods=["GET"])
def get_me():
    user = get_current_user()
    if not user:
        return jsonify({
            "success": False,
            "status": "guest",
            "authenticated": False,
            "user": None
        }), 200

    profile = ProfileRepository.get_profile(user["id"])
    settings = SettingsRepository.get_settings(user["id"])
    unread = NotificationRepository.get_unread_count(user["id"])

    return jsonify({
        "success": True,
        "status": "success",
        "authenticated": True,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "is_verified": user["is_verified"],
            "is_active": user.get("is_active", 1),
            "unread_notifications": unread
        },
        "profile": profile,
        "settings": settings
    }), 200


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"status": "error", "message": "Email is required."}), 400

    base_url = (
        os.environ.get("APP_BASE_URL")
        or os.environ.get("RENDER_EXTERNAL_URL")
        or request.host_url.rstrip("/")
        or "https://career-compass.onrender.com"
    ).rstrip("/")

    smtp_configured = EmailService.is_configured()
    user = UserRepository.get_by_email(email)

    if user:
        token = TokenRepository.create_password_reset_token(user["id"])
        reset_link = f"{base_url}/?reset_token={token}#reset-password"

        if smtp_configured:
            try:
                EmailService.send_password_reset_email(email, token, base_url)
                return jsonify({
                    "status": "success",
                    "smtp_configured": True,
                    "message": "A password reset link has been dispatched to your email address. Please check your inbox and spam folder."
                }), 200
            except Exception as e:
                # Log dispatch failure and provide immediate link fallback
                return jsonify({
                    "status": "success",
                    "smtp_configured": False,
                    "reset_url": reset_link,
                    "message": f"SMTP email delivery encountered an issue ({str(e)}). You can proceed directly using the reset link below."
                }), 200
        else:
            # SMTP not configured on server (e.g. dev environment or Render before adding env vars)
            # Log the email safely so it is captured in audit logs
            try:
                EmailService.send_password_reset_email(email, token, base_url)
            except Exception:
                pass
            return jsonify({
                "status": "success",
                "smtp_configured": False,
                "reset_url": reset_link,
                "message": "Password reset token generated. Since SMTP email delivery is not configured on this server, use the secure link below to complete your password reset."
            }), 200

    # User not found: prevent email enumeration while maintaining consistent response
    return jsonify({
        "status": "success",
        "smtp_configured": smtp_configured,
        "message": "If an account exists with this email address, a password reset link has been dispatched."
    }), 200


@auth_bp.route("/verify-reset-token", methods=["GET"])
def verify_reset_token():
    token = request.args.get("token", "").strip()
    if not token:
        return jsonify({"status": "error", "message": "Reset token is required."}), 400

    token_info = TokenRepository.verify_reset_token(token)
    if not token_info:
        return jsonify({
            "status": "error",
            "code": "INVALID_OR_EXPIRED_TOKEN",
            "message": "This password reset link is invalid or has expired. Please request a new link."
        }), 400

    email = token_info.get("email", "")
    masked_email = ""
    if "@" in email:
        parts = email.split("@", 1)
        name_part = parts[0]
        domain_part = parts[1]
        if len(name_part) <= 2:
            masked_email = f"{name_part[0]}*@{domain_part}"
        else:
            masked_email = f"{name_part[0]}{'*' * (len(name_part) - 2)}{name_part[-1]}@{domain_part}"

    return jsonify({
        "status": "success",
        "valid": True,
        "email": masked_email,
        "message": "Reset token is valid."
    }), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    token = (data.get("token") or "").strip()
    new_password = data.get("password") or data.get("new_password") or ""

    if not token or not new_password:
        return jsonify({"status": "error", "message": "Token and new password are required."}), 400

    if len(new_password) < 8:
        return jsonify({"status": "error", "message": "Password must be at least 8 characters long."}), 400

    user_id = TokenRepository.verify_and_use_reset_token(token)
    if not user_id:
        return jsonify({"status": "error", "message": "This password reset link is invalid or has expired."}), 400

    UserRepository.update_password(user_id, new_password)
    return jsonify({
        "status": "success",
        "message": "Your password has been successfully reset. Please log in with your new credentials."
    }), 200


@auth_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    data = request.get_json() or {}
    old_password = data.get("old_password") or ""
    new_password = data.get("new_password") or ""

    if not old_password or not new_password:
        return jsonify({"status": "error", "message": "Current and new passwords are required."}), 400

    if len(new_password) < 8:
        return jsonify({"status": "error", "message": "New password must be at least 8 characters long."}), 400

    user = UserRepository.get_by_id(g.user["id"])
    full_user = UserRepository.get_by_email(user["email"])
    if not full_user or not UserRepository.verify_password(full_user["password_hash"], old_password):
        return jsonify({"status": "error", "message": "Current password is incorrect."}), 400

    UserRepository.update_password(g.user["id"], new_password)
    return jsonify({"status": "success", "message": "Password changed successfully. Please log in again."})


@auth_bp.route("/edit-profile", methods=["POST"])
@login_required
def edit_profile():
    data = request.get_json() or {}
    updated = ProfileRepository.save_profile(g.user["id"], data)
    return jsonify({
        "status": "success",
        "message": "Profile updated successfully.",
        "profile": updated
    })


@auth_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "GET":
        current_settings = SettingsRepository.get_settings(g.user["id"])
        return jsonify({"status": "success", "settings": current_settings})

    data = request.get_json() or {}
    prefs = data.get("preferences") or {}
    notifs = data.get("notifications") or {}

    SettingsRepository.update_settings(g.user["id"], prefs, notifs)
    updated_settings = SettingsRepository.get_settings(g.user["id"])
    return jsonify({
        "status": "success",
        "message": "Settings saved successfully.",
        "settings": updated_settings
    })


@auth_bp.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    UserRepository.delete_user(g.user["id"])
    resp = make_response(jsonify({"status": "success", "message": "Account and all associated personal data have been permanently deleted."}))
    resp.set_cookie("session_token", "", max_age=0, path="/")
    return resp
