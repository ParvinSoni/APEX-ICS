import curses

# Initialize the curses screen
screen = curses.initscr()

# Set some basic screen options
curses.noecho()
curses.cbreak()
screen.keypad(True)

# Add some basic status information to the screen
screen.addstr(0, 0, "Fuzzing Status:")
screen.addstr(1, 0, "================")

# Define a function to update the status screen
def update_status(packet_count, crashes_found, unique_crashes_found):
    screen.addstr(3, 0, f"Packets sent: {packet_count}")
    screen.addstr(4, 0, f"Crashes found: {crashes_found}")
    screen.addstr(5, 0, f"Unique crashes found: {unique_crashes_found}")
    screen.refresh()

# Call the update_status function periodically to update the screen
update_status(100, 2, 1)

# Wait for user input before exiting
screen.getch()

# Restore the terminal settings
curses.nocbreak()
screen.keypad(False)
curses.echo()
curses.endwin()
