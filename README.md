# Input Activity Monitor

A Python-based tool that monitors keyboard and mouse activity to track active computer usage time with configurable time limits and alerts.

## Overview

This tool helps users track their active computer usage time by monitoring keyboard and mouse inputs. It features:
- Real-time progress tracking
- Configurable time limits
- Visual progress bar
- Sound alerts
- Detailed activity logging
- Mouse and keyboard input detection

## Installation

### Prerequisites
- Python 3.6 or higher
- pyxhook library (for input monitoring)
- PulseAudio (optional, for sound alerts)

### Installing Dependencies

1. Install required Python packages:
```bash
pip install pyxhook
```

2. For sound alerts on Linux systems, ensure PulseAudio is installed:
```bash
# On Debian/Ubuntu
sudo apt-get install pulseaudio

# On Fedora
sudo dnf install pulseaudio
```

## Usage

### Basic Command

```bash
python3 act.py -tm TIME_LIMIT
```

### Time Limit Format

The time limit should be specified in the format: `XhYmZs` where:
- `X` = hours (optional)
- `Y` = minutes (optional)
- `Z` = seconds (optional)

Examples:
```bash
# Set 1 hour limit
python3 act.py -tm 1h

# Set 30 minute limit
python3 act.py -tm 30m

# Set 1 hour and 30 minute limit
python3 act.py -tm 1h30m

# Set 1 hour, 30 minutes, and 15 seconds limit
python3 act.py -tm 1h30m15s
```

## Features

### Progress Bar
The tool displays a real-time progress bar showing:
- Active time elapsed
- Total time limit
- Remaining time
- Activity indicator (`*` when input is detected)
- Alert count

Example:
```
[========--------] * 00:15:30/01:00:00 (Remaining: 00:44:30)
```

### Activity Logging
Activity is automatically logged to `/tmp/input_activity.log` with the following information:
- Timestamp and event type
- Session duration
- Total active time
- Time limit
- Remaining time
- Activity rate (percentage of active time)
- Alert status
- Current status

Log entries are written:
- When the session starts
- Every 30 seconds during active use
- When time limit alerts occur
- When the session ends

### Alerts
The system provides audio alerts when the time limit is reached:
- Up to 5 alerts will sound
- Uses PulseAudio for sound (falls back to console beep)
- Session automatically ends after the maximum number of alerts

## Understanding the Output

### Progress Bar Components
```
[========--------] * 00:15:30/01:00:00 (Remaining: 00:44:30) (Alerts: 1/5)
   ^                ^     ^       ^          ^                    ^
   |                |     |       |          |                    |
   Progress         |     |       |          |                    Number of alerts
   indicator        |     |       |          Remaining time
                    |     |       Total time limit
                    |     Elapsed time
                    Activity indicator
```

### Log File Format
```
[2024-10-26 10:00:00] - Regular Update
  Session Duration: 00:15:30
  Total Active Time: 00:10:45
  Time Limit: 01:00:00
  Remaining Time: 00:49:15
  Activity Rate: 69.5%
  Alerts Played: 0/5
  Status: Active
==================================================
```

## Technical Details

### Activity Detection
- Keyboard events: All keystrokes
- Mouse events:
  - All button clicks
  - Movement (filtered to prevent over-counting)
- Activity is counted when inputs occur within 1 second of each other

### Time Tracking
- Active time is only accumulated during actual input activity
- Idle periods are not counted towards the time limit
- Mouse movements are debounced (100ms threshold)

## Limitations

- Requires X11 (Linux/Unix systems)
- Must be run with appropriate permissions to monitor input
- Log file is stored in `/tmp` directory (may be cleared on system restart)
- No pause/resume functionality

## Troubleshooting

1. **No sound alerts:**
   - Check if PulseAudio is installed and running
   - Verify sound file exists: `/usr/share/sounds/freedesktop/stereo/complete.oga`
   - System will fall back to console beep if audio fails

2. **Permission errors:**
   - Ensure script has permission to read input devices
   - Run with appropriate user permissions

3. **High CPU usage:**
   - Adjust mouse movement threshold if needed
   - Check system load during idle periods

## Contributing

Feel free to submit issues and enhancement requests!
