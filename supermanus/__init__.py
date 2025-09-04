# SuperManUS TaskEnforcer Package
# Universal LLM Task Discipline System

__version__ = "1.0.0"
__author__ = "SuperManUS Team"
__description__ = "Universal LLM Task Discipline System - Solving the 90% LLM deviation problem"

from .task_enforcer import TaskSystemEnforcer
from .llm_guard import LLMGuard

__all__ = ["TaskSystemEnforcer", "LLMGuard"]