"""Entry point for running the quiz automation GUI."""
from __future__ import annotations

from quiz_automation.gui import QuizGUI


if __name__ == "__main__":
    gui = QuizGUI()
    gui.run()
