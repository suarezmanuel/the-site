import subprocess
import time
import datetime
import platform

# --- Configuration ---
HOST_TO_PING = "8.8.8.8"  # Google's Public DNS - very reliable
LOG_FILE = "connectivity_log.txt"
SLEEP_INTERVAL = 1  # Seconds to wait between pings
PING_TIMEOUT = 1    # Seconds to wait for a response

def log_message(message):
    """Prints a message to the console and appends it to the log file."""
    # Get a nicely formatted timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] - {message}"
    
    # Print to the console
    print(log_entry)
    
    # Write to the log file
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry + "\n")

def check_connection(host):
    """
    Returns True if the host responds to a ping, False otherwise.
    Uses OS-specific ping command for compatibility.
    """
    # Determine the correct ping command based on the operating system
    # -n 1 for Windows, -c 1 for Linux/macOS (send only 1 packet)
    # -w 1000 for Windows (1000 ms timeout), -W 1 for Linux/macOS (1 sec timeout)
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    timeout_param = '-w' if platform.system().lower() == 'windows' else '-W'
    timeout_value = '1000' if platform.system().lower() == 'windows' else str(PING_TIMEOUT)

    command = ['ping', param, '1', timeout_param, timeout_value, host]

    # Run the command, hiding the output (stdout and stderr)
    # The return code will be 0 for success and non-zero for failure
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception as e:
        log_message(f"An error occurred: {e}")
        return False


# --- Main Program Loop ---
if __name__ == "__main__":
    log_message("Starting connectivity check...")
    try:
        while True:
            if check_connection(HOST_TO_PING):
                log_message("Connection SUCCESSFUL.")
            else:
                log_message("Connection FAILED.")
            
            # Wait for the specified interval before trying again
            time.sleep(SLEEP_INTERVAL)
            
    except KeyboardInterrupt:
        # This allows you to stop the script gracefully with Ctrl+C
        log_message("Connectivity check stopped by user.")
        print("Exiting.")