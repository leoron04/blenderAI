from __future__ import annotations

from blenderAI import operators, ui


class _DummyLayout:
    def box(self):
        return self

    def column(self, align=False):
        return self

    def row(self, align=False):
        return self

    def prop(self, *args, **kwargs):
        return None

    def label(self, *args, **kwargs):
        return None

    def operator(self, *args, **kwargs):
        return type("Op", (), {"bl_idname": "dummy"})


def test_main_panel_draw_uses_layout(fake_context):
    panel = ui.BLENDER_AI_PT_main_panel()
    panel.layout = _DummyLayout()

    panel.draw(fake_context)

    assert hasattr(panel, "layout")


def test_preview_operator_updates_scene(fake_context):
    op = operators.BLENDER_AI_OT_preview_code()
    op.code = "print('ok')"
    op.description = "desc"

    result = op.execute(fake_context)

    assert result == {"FINISHED"}
    assert fake_context.scene.ai_preview_code == "print('ok')"
    assert fake_context.scene.ai_preview_description == "desc"


def test_apply_preview_without_code_returns_cancelled(fake_context):
    op = operators.BLENDER_AI_OT_apply_preview()
    fake_context.scene.ai_preview_code = ""

    result = op.execute(fake_context)

    assert result == {"CANCELLED"}


def test_auto_rig_operator_sets_preview(fake_context):
    op = operators.BLENDER_AI_OT_auto_rig()

    result = op.execute(fake_context)

    assert result == {"FINISHED"}
    assert "Auto-rig" in fake_context.scene.ai_preview_description
    assert "Auto-rig" in fake_context.scene.ai_preview_code
