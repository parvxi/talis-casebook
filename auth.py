"""Supabase Auth helpers.

The signed-in user is kept in st.session_state["user"] as {"id", "email"}. It is only
ever set from a successful Supabase response, so the user id cannot be supplied by
the browser.
"""

import streamlit as st
from supabase import Client, ClientOptions, create_client
from supabase_auth.errors import AuthError


def _client() -> Client:
    # One client per browser session (not cached globally) so users never share auth state.
    if "supabase" not in st.session_state:
        st.session_state.supabase = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_ANON_KEY"],
            options=ClientOptions(persist_session=False, auto_refresh_token=False),
        )
    return st.session_state.supabase


def _error_text(exc: Exception) -> str:
    if isinstance(exc, AuthError):
        return getattr(exc, "message", None) or str(exc)
    return "Could not reach the sign-in service. Please try again."


def _remember(user) -> None:
    st.session_state.user = {"id": str(user.id), "email": user.email}


def current_user() -> dict | None:
    return st.session_state.get("user")


def sign_in(email: str, password: str) -> str | None:
    """Returns an error message, or None on success."""
    try:
        response = _client().auth.sign_in_with_password({"email": email, "password": password})
    except Exception as exc:
        return _error_text(exc)
    _remember(response.user)
    return None


def sign_up(email: str, password: str) -> str | None:
    """Returns an error message, or None on success (the user is signed in straight away)."""
    try:
        response = _client().auth.sign_up({"email": email, "password": password})
    except Exception as exc:
        return _error_text(exc)
    if response.session is None:
        return "Account created, but this project requires email confirmation before sign-in."
    _remember(response.user)
    return None


def sign_out() -> None:
    try:
        _client().auth.sign_out()
    except Exception:
        pass  # the local session is cleared either way
    st.session_state.pop("user", None)


def require_user() -> dict:
    """Server-side guard: call first in every handler that runs SQL or saves an answer."""
    user = current_user()
    if not user:
        st.error("Please sign in first.")
        st.stop()
    return user
