from __future__ import annotations

import sys
import types

# Pytest importa questo file come parte del package, che forza l'import di __init__.py.
# Installiamo un mock minimale di bpy per evitare errori di import durante la raccolta.
if "bpy" not in sys.modules:
    sys.modules["bpy"] = types.SimpleNamespace(
        types=types.SimpleNamespace(Operator=object, Panel=object, Scene=object, Object=object, Context=object),
        props=types.SimpleNamespace(
            StringProperty=lambda **kwargs: kwargs.get("default", ""),
            BoolProperty=lambda **kwargs: kwargs.get("default", False),
            EnumProperty=lambda **kwargs: kwargs.get("default", None),
            IntProperty=lambda **kwargs: kwargs.get("default", 0),
            FloatProperty=lambda **kwargs: kwargs.get("default", 0.0),
        ),
        data=types.SimpleNamespace(materials=[], lights=[], cameras=[], collections=[]),
        utils=types.SimpleNamespace(register_class=lambda cls: None, unregister_class=lambda cls: None),
    )

collect_ignore = ["test_runner.py"]
