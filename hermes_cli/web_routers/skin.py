"""Skin/banner info routes for the dashboard UI.

Exposes the active skin's branding, banner_logo, banner_hero, and colors
so React components can render a welcome banner matching the CLI/TUI.
"""

from fastapi import APIRouter

from hermes_cli.web_deps import late

router = APIRouter()

# Late-bound to avoid import cycles at module load time.
_config_profile_scope = late("_config_profile_scope", "hermes_cli.web_server_profiles")


@router.get("/api/skin")
async def get_active_skin() -> dict:
    """Return the active skin's branding and banner data."""
    try:
        profile_scope = _config_profile_scope()
        if profile_scope is not None:
            # In a multi-profile context, the profile scope knows which profile's config to use.
            # The skin_engine module uses load_config() which reads the active profile's config.
            # We need to temporarily bind the profile scope for the skin resolution.
            from hermes_cli.config import load_config
            from hermes_cli.skin_engine import init_skin_from_config, get_active_skin
            cfg = load_config()
            init_skin_from_config(cfg)
            skin = get_active_skin()
        else:
            from hermes_cli.skin_engine import get_active_skin
            skin = get_active_skin()

        if skin is None:
            return {"error": "No active skin", "name": "default"}

        # Return only the fields the dashboard needs. SkinConfig is a dataclass,
        # so access attributes directly (not .get()).
        return {
            "name": skin.name,
            "description": skin.description,
            "branding": skin.branding,
            "banner_logo": skin.banner_logo,
            "banner_hero": skin.banner_hero,
            "colors": skin.colors,
            "light_colors": skin.light_colors,
            "dark_colors": skin.dark_colors,
            "tool_prefix": skin.tool_prefix,
            "help_header": skin.help_header if hasattr(skin, "help_header") else "",
            "spinner": skin.spinner,
        }
    except Exception as e:
        # Fail gracefully — the UI will fall back to hardcoded defaults
        return {"error": str(e), "name": "default"}