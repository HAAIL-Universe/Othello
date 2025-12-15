class ShadowManager:
    """Stub shadow manager to absorb shadow updates without external dependencies."""

    def __init__(self) -> None:
        self.shadow_state = {}

    def safe_update(self, payload, consent_level="auto"):
        # Merge payload into in-memory shadow_state; ignored persistence for now.
        try:
            if isinstance(payload, dict):
                self.shadow_state.update(payload)
        except Exception:
            pass
        return self.shadow_state
