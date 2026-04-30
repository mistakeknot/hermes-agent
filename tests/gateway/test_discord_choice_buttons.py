from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import sys

import pytest

from gateway.config import PlatformConfig


class _FakeView:
    def __init__(self, *, timeout=None):
        self.timeout = timeout
        self.children = []

    def add_item(self, item):
        self.children.append(item)


class _FakeButton:
    def __init__(self, *, label, style=None, custom_id=None):
        self.label = label
        self.style = style
        self.custom_id = custom_id
        self.disabled = False
        self.callback = None


class _FakeResponse:
    def __init__(self):
        self.edit_message = AsyncMock()
        self.send_message = AsyncMock()


def _ensure_discord_mock():
    if "discord" in sys.modules and hasattr(sys.modules["discord"], "__file__"):
        return

    discord_mod = MagicMock()
    discord_mod.Intents.default.return_value = MagicMock()
    discord_mod.Client = MagicMock
    discord_mod.File = MagicMock
    discord_mod.DMChannel = type("DMChannel", (), {})
    discord_mod.Thread = type("Thread", (), {})
    discord_mod.ForumChannel = type("ForumChannel", (), {})
    discord_mod.ui = SimpleNamespace(
        View=_FakeView,
        button=lambda *a, **k: (lambda fn: fn),
        Button=_FakeButton,
    )
    discord_mod.ButtonStyle = SimpleNamespace(
        success="success",
        primary="primary",
        secondary="secondary",
        danger="danger",
        green="green",
        grey="grey",
        blurple="blurple",
        red="red",
    )
    discord_mod.Color = SimpleNamespace(
        orange=lambda: "orange",
        green=lambda: "green",
        blue=lambda: "blue",
        red=lambda: "red",
        purple=lambda: "purple",
        gold=lambda: "gold",
        greyple=lambda: "greyple",
    )
    discord_mod.Interaction = object
    discord_mod.Embed = MagicMock
    discord_mod.app_commands = SimpleNamespace(
        describe=lambda **kwargs: (lambda fn: fn),
        choices=lambda **kwargs: (lambda fn: fn),
        Choice=lambda **kwargs: SimpleNamespace(**kwargs),
    )

    ext_mod = MagicMock()
    commands_mod = MagicMock()
    commands_mod.Bot = MagicMock
    ext_mod.commands = commands_mod

    sys.modules.setdefault("discord", discord_mod)
    sys.modules.setdefault("discord.ext", ext_mod)
    sys.modules.setdefault("discord.ext.commands", commands_mod)


_ensure_discord_mock()

import gateway.platforms.discord as discord_platform  # noqa: E402
from gateway.platforms.discord import (  # noqa: E402
    ChoiceCardView,
    DiscordAdapter,
    _extract_choice_button_labels,
)


def test_extract_choice_button_labels_from_contract_line():
    content = """**Next — response-card**

**Recommendation:** Continue.

Buttons: [Proceed] [Show options] [Handoff packet] [Pause]
"""

    assert _extract_choice_button_labels(content) == [
        "Proceed",
        "Show options",
        "Handoff packet",
        "Pause",
    ]


def test_extract_choice_button_labels_rejects_too_many_options():
    content = "Buttons: [One] [Two] [Three] [Four] [Five]"

    assert _extract_choice_button_labels(content) == []


def test_extract_choice_button_labels_rejects_duplicate_and_command_labels():
    assert _extract_choice_button_labels("Buttons: [Proceed] [proceed]") == []
    assert _extract_choice_button_labels("Buttons: [/stop] [Proceed]") == []


@pytest.mark.asyncio
async def test_send_attaches_choice_view_and_keeps_text_fallback(monkeypatch):
    created_views = []

    class FakeChoiceCardView:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            created_views.append(self)

    monkeypatch.setattr(discord_platform, "ChoiceCardView", FakeChoiceCardView)

    adapter = DiscordAdapter(PlatformConfig(enabled=True, token="[REDACTED]"))
    adapter._allowed_user_ids = {"42"}
    sent_msg = SimpleNamespace(id=1234)
    channel = SimpleNamespace(
        id=222,
        name="work-thread",
        guild=SimpleNamespace(name="Test Guild"),
        topic=None,
        send=AsyncMock(return_value=sent_msg),
    )
    adapter._client = SimpleNamespace(
        get_channel=lambda _chat_id: channel,
        fetch_channel=AsyncMock(),
    )

    card = """**Next — response-card**

**Recommendation:** Continue.
**Risk/approval:** No restart yet.

Buttons: [Proceed] [Show options] [Handoff packet] [Pause]
"""

    result = await adapter.send("111", card, metadata={"thread_id": "222"})

    assert result.success is True
    assert result.message_id == "1234"
    assert len(created_views) == 1
    view = created_views[0]
    assert view.kwargs["choices"] == [
        "Proceed",
        "Show options",
        "Handoff packet",
        "Pause",
    ]
    assert view.kwargs["content"] == card
    assert view.kwargs["chat_id"] == "222"
    assert view.kwargs["thread_id"] == "222"
    assert view.kwargs["allowed_user_ids"] == {"42"}
    send_kwargs = channel.send.await_args.kwargs
    assert send_kwargs["content"] == card
    assert send_kwargs["view"] is view


@pytest.mark.asyncio
async def test_send_attaches_choice_view_to_actual_chunk_when_message_splits(monkeypatch):
    created_views = []

    class FakeChoiceCardView:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            created_views.append(self)

    monkeypatch.setattr(discord_platform, "ChoiceCardView", FakeChoiceCardView)

    adapter = DiscordAdapter(PlatformConfig(enabled=True, token="[REDACTED]"))
    adapter.MAX_MESSAGE_LENGTH = 80
    send_count = 0

    async def fake_send(**_kwargs):
        nonlocal send_count
        send_count += 1
        return SimpleNamespace(id=1000 + send_count)

    channel = SimpleNamespace(
        id=222,
        name="work-thread",
        guild=SimpleNamespace(name="Test Guild"),
        topic=None,
        send=AsyncMock(side_effect=fake_send),
    )
    adapter._client = SimpleNamespace(
        get_channel=lambda _chat_id: channel,
        fetch_channel=AsyncMock(),
    )
    card = (
        "**Next — response-card**\n\n"
        "**Recommendation:** Continue with a long enough explanation to split.\n\n"
        + ("A" * 120)
        + "\n\nButtons: [Proceed] [Pause]"
    )

    result = await adapter.send("222", card)

    assert result.success is True
    assert channel.send.await_count > 1
    last_send_kwargs = channel.send.await_args.kwargs
    assert len(created_views) == 1
    assert created_views[0].kwargs["content"] == last_send_kwargs["content"]
    assert created_views[0].kwargs["content"] != card


@pytest.mark.asyncio
async def test_send_does_not_attach_choice_view_for_invalid_button_count(monkeypatch):
    class FakeChoiceCardView:
        def __init__(self, **_kwargs):
            raise AssertionError("ChoiceCardView should not be constructed")

    monkeypatch.setattr(discord_platform, "ChoiceCardView", FakeChoiceCardView)

    adapter = DiscordAdapter(PlatformConfig(enabled=True, token="[REDACTED]"))
    channel = SimpleNamespace(
        id=222,
        send=AsyncMock(return_value=SimpleNamespace(id=1234)),
    )
    adapter._client = SimpleNamespace(
        get_channel=lambda _chat_id: channel,
        fetch_channel=AsyncMock(),
    )

    result = await adapter.send("222", "Buttons: [One] [Two] [Three] [Four] [Five]")

    assert result.success is True
    assert "view" not in channel.send.await_args.kwargs


def _make_view(adapter, *, allowed_user_ids=None, resolved=False, expired=False):
    adapter._allowed_user_ids = set(allowed_user_ids or [])
    if not hasattr(adapter, "_allowed_role_ids"):
        adapter._allowed_role_ids = set()
    view = ChoiceCardView.__new__(ChoiceCardView)
    view.adapter = adapter
    view.content = "Buttons: [Proceed] [Pause]"
    view.choices = ["Proceed", "Pause"]
    view.chat_id = "222"
    view.chat_name = "Test Guild / #agent-ops / work-thread"
    view.chat_type = "thread"
    view.thread_id = "222"
    view.chat_topic = None
    view.allowed_user_ids = set(allowed_user_ids or [])
    view.resolved = resolved
    view.expired = expired
    view.children = [SimpleNamespace(disabled=False), SimpleNamespace(disabled=False)]
    return view


def _make_interaction(*, user_id="42", display_name="operator"):
    return SimpleNamespace(
        user=SimpleNamespace(id=user_id, display_name=display_name, name=display_name, bot=False),
        channel=SimpleNamespace(
            id=222,
            name="work-thread",
            guild=SimpleNamespace(name="Test Guild"),
            parent=SimpleNamespace(name="agent-ops", guild=SimpleNamespace(name="Test Guild")),
            topic=None,
        ),
        channel_id=222,
        message=SimpleNamespace(id=777, content="Buttons: [Proceed] [Pause]", embeds=[]),
        response=_FakeResponse(),
    )


@pytest.mark.asyncio
async def test_choice_button_routes_authorized_click_to_same_session():
    adapter = DiscordAdapter(PlatformConfig(enabled=True, token="[REDACTED]"))
    adapter.handle_message = AsyncMock()
    view = _make_view(adapter, allowed_user_ids={"42"})
    interaction = _make_interaction()

    await ChoiceCardView._on_choice_selected(view, interaction, "Proceed")

    interaction.response.edit_message.assert_awaited_once()
    interaction.response.send_message.assert_not_awaited()
    for child in view.children:
        assert child.disabled is True
    adapter.handle_message.assert_awaited_once()
    event = adapter.handle_message.await_args.args[0]
    assert event.text == "Proceed"
    assert event.message_id == "777"
    assert event.source.chat_id == "222"
    assert event.source.thread_id == "222"
    assert event.source.user_id == "42"
    assert event.source.user_name == "operator"


@pytest.mark.asyncio
async def test_choice_button_allows_role_authorized_click_to_same_session():
    adapter = DiscordAdapter(PlatformConfig(enabled=True, token="[REDACTED]"))
    adapter._allowed_user_ids = set()
    adapter._allowed_role_ids = {7}
    adapter.handle_message = AsyncMock()
    view = _make_view(adapter)
    interaction = _make_interaction()
    interaction.user.roles = [SimpleNamespace(id=7)]

    await ChoiceCardView._on_choice_selected(view, interaction, "Proceed")

    interaction.response.edit_message.assert_awaited_once()
    interaction.response.send_message.assert_not_awaited()
    adapter.handle_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_choice_button_rejects_unauthorized_click_without_routing():
    adapter = DiscordAdapter(PlatformConfig(enabled=True, token="[REDACTED]"))
    adapter.handle_message = AsyncMock()
    view = _make_view(adapter, allowed_user_ids={"99"})
    interaction = _make_interaction(user_id="42")

    await ChoiceCardView._on_choice_selected(view, interaction, "Proceed")

    interaction.response.send_message.assert_awaited_once()
    interaction.response.edit_message.assert_not_awaited()
    adapter.handle_message.assert_not_awaited()
    assert view.resolved is False


@pytest.mark.asyncio
async def test_choice_button_rejects_bot_click_without_routing():
    adapter = DiscordAdapter(PlatformConfig(enabled=True, token="[REDACTED]"))
    adapter.handle_message = AsyncMock()
    view = _make_view(adapter)
    interaction = _make_interaction(user_id="4242", display_name="OtherBot")
    interaction.user.bot = True

    await ChoiceCardView._on_choice_selected(view, interaction, "Proceed")

    interaction.response.send_message.assert_awaited_once()
    interaction.response.edit_message.assert_not_awaited()
    adapter.handle_message.assert_not_awaited()
    assert view.resolved is False


@pytest.mark.asyncio
async def test_choice_button_rejects_expired_click_without_routing():
    adapter = DiscordAdapter(PlatformConfig(enabled=True, token="[REDACTED]"))
    adapter.handle_message = AsyncMock()
    view = _make_view(adapter, allowed_user_ids={"42"}, expired=True)
    interaction = _make_interaction()

    await ChoiceCardView._on_choice_selected(view, interaction, "Proceed")

    interaction.response.send_message.assert_awaited_once()
    interaction.response.edit_message.assert_not_awaited()
    adapter.handle_message.assert_not_awaited()


def test_choice_buttons_are_not_exposed_as_broad_discord_tool_actions():
    from tools import discord_tool

    forbidden_action_names = {
        "choice_button",
        "choice_card",
        "click_button",
        "quick_reply",
        "send_choice_card",
        "send_quick_reply",
    }

    assert forbidden_action_names.isdisjoint(discord_tool._ACTIONS)
    assert forbidden_action_names.isdisjoint(discord_tool._ACTION_MANIFEST)
