"""Entry point for the quiz automation GUI."""

from quiz_automation.gui import QuizGUI


def main() -> None:
    """Run the GUI."""
    gui = QuizGUI()
    gui.run()


if __name__ == "__main__":
    main()
