"""Main entry point for PID-Tag Puller application."""

from gui.main_window import MainWindow


def main():
    """Launch the application."""
    app = MainWindow()

    # Bring window to front on macOS
    app.lift()
    app.attributes('-topmost', True)
    app.after(100, lambda: app.attributes('-topmost', False))

    # Focus the window
    app.focus_force()

    app.mainloop()


if __name__ == "__main__":
    main()
