"""Verify the interactive replay-mode banner contract in the component source."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENT = (ROOT / "components" / "ReplayNotice.tsx").read_text()
HOME = (ROOT / "app" / "page.tsx").read_text()

EXPANDED_TEXT = (
    "Replay mode uses sanitized saved outputs from the completed sourcing run. "
    "It does not initiate new X API requests, no API credential is deployed, and "
    "no additional API spending can occur. This keeps the demonstration stable "
    "and reproducible."
)


def test_uses_semantic_button_with_aria():
    assert 'type="button"' in COMPONENT
    assert "aria-expanded={open}" in COMPONENT
    assert "aria-controls={contentId}" in COMPONENT
    assert 'id={contentId}' in COMPONENT
    assert "useId()" in COMPONENT


def test_toggle_state_and_hidden_semantics():
    assert "useState(false)" in COMPONENT  # default collapsed
    assert "setOpen((v) => !v)" in COMPONENT  # click toggles
    assert "hidden={!open}" in COMPONENT  # hidden from a11y tree when collapsed


def test_chevron_present_and_rotates():
    assert "chevron" in COMPONENT
    assert 'open ? " up" : ""' in COMPONENT


def test_expanded_text_matches_spec():
    normalized = " ".join(COMPONENT.split())
    assert " ".join(EXPANDED_TEXT.split()) in normalized


def test_home_enables_expandable_others_do_not():
    assert "<ReplayNotice expandable />" in HOME
    # non-home usages keep the static, non-interactive banner
    assert "expandable = false" in COMPONENT


def test_no_navigation_or_new_tab_or_live_api():
    assert "href" not in COMPONENT
    assert "target=" not in COMPONENT
    assert "api.x.com" not in COMPONENT
    assert "fetch(" not in COMPONENT


def test_no_em_dashes_in_component():
    assert "—" not in COMPONENT and "–" not in COMPONENT
