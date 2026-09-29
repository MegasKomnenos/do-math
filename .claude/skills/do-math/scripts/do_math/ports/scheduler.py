"""Scheduler port: run one action of the do-math task-scheduler adapter.

``arguments`` are the adapter's named parameters (Repository, Instance,
Workspace, Python, OperatorTask, EngineTask, WakeTask and the action's extras),
in the order the adapter receives them. Every action answers the three task
views ``{"operator": view|None, "engine": view|None, "wake": view|None}``.
"""
from typing import Protocol


class Scheduler(Protocol):
    def run(self, action: str, arguments: dict) -> dict:
        """The adapter's JSON object after ``action``; a failed action raises RuntimeError."""
