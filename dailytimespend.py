#!/usr/bin/env python3
import argparse
import time
from datetime import datetime, timedelta
import pyxhook
import os
import re
import subprocess
from pathlib import Path
import threading
import sys

class InputMonitor:
    def __init__(self, time_limit):
        self.start_time = datetime.now()
        self.last_activity = None
        self.is_active = False
        self.total_active_time = timedelta()
        self.time_limit = time_limit
        self.log_file = Path("/tmp/input_activity.log")
        self.running = True
        self.activity_lock = threading.Lock()
        self.alert_count = 0
        self.max_alerts = 5
        self.last_log_time = datetime.now()
        self.log_interval = timedelta(seconds=2)  # Log every 30 seconds
        
        # Initialize hooks
        self.hook_manager = pyxhook.HookManager()
        self.hook_manager.KeyDown = self.handle_keyboard
        self.hook_manager.MouseAllButtonsDown = self.handle_mouse_click
        self.hook_manager.MouseMovement = self.handle_mouse_movement
        
    @staticmethod
    def parse_time_limit(time_str):
        """Parse time string in format like 1h10m01s"""
        pattern = r'(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
        match = re.match(pattern, time_str)
        if not match:
            raise ValueError("Invalid time format. Use format like 1h10m01s")
            
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
        
    def format_timedelta(self, td):
        """Format timedelta into HH:MM:SS"""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def handle_keyboard(self, event):
        """Handle keyboard events"""
        with self.activity_lock:
            current_time = datetime.now()
            if self.last_activity is None:
                self.last_activity = current_time
            else:
                # Add the time since last activity if it's within 1 second
                time_diff = current_time - self.last_activity
                if time_diff.total_seconds() <= 1.0:
                    self.total_active_time += time_diff
            self.last_activity = current_time
            self.is_active = True
            self.check_time_limit()
            self.check_log_update()

    def handle_mouse_click(self, event):
        """Handle mouse click events"""
        self.handle_keyboard(event)  # Reuse the same logic

    def handle_mouse_movement(self, event):
        """Handle mouse movement events"""
        current_time = datetime.now()
        
        # Only count mouse movement if it's been more than 100ms since last movement
        if (self.last_activity is None or 
            (current_time - self.last_activity).total_seconds() > 0.1):
            self.handle_keyboard(event)
            
    def check_time_limit(self):
        """Check if time limit has been reached"""
        if self.total_active_time >= self.time_limit:
            if self.alert_count < self.max_alerts:
                self.play_alert()
                self.alert_count += 1
                self.log_activity("Time Limit Alert")
                
            if self.alert_count >= self.max_alerts:
                self.running = False
                self.log_activity("Session Ended - Time Limit Reached")
                print(f"\nTime limit of {self.time_limit} reached! (Alert limit reached)")
                self.hook_manager.cancel()

    def check_log_update(self):
        """Check if it's time to update the log"""
        current_time = datetime.now()
        if current_time - self.last_log_time >= self.log_interval:
            self.log_activity("Regular Update")
            self.last_log_time = current_time
        
    def draw_progress_bar(self):
        """Draw progress bar with remaining time"""
        while self.running:
            remaining_time = self.time_limit - self.total_active_time
            if remaining_time.total_seconds() <= 0:
                break
                
            # Calculate progress
            progress = (self.total_active_time.total_seconds() / 
                      self.time_limit.total_seconds())
            bar_length = 40
            filled_length = int(bar_length * progress)
            
            # Create the bar
            bar = ('=' * filled_length) + ('-' * (bar_length - filled_length))
            
            # Format times
            elapsed = self.format_timedelta(self.total_active_time)
            remaining = self.format_timedelta(remaining_time)
            total = self.format_timedelta(self.time_limit)
            
            # Add activity indicator and alert count if relevant
            activity_indicator = "*" if self.is_active else " "
            alert_info = f" (Alerts: {self.alert_count}/{self.max_alerts})" if self.alert_count > 0 else ""
            
            # Clear line and draw progress
            sys.stdout.write('\r')
            sys.stdout.write(f'[{bar}] {activity_indicator} {elapsed}/{total} (Remaining: {remaining}){alert_info}')
            sys.stdout.flush()
            
            # Reset activity flag after displaying
            self.is_active = False
            time.sleep(0.1)
            
    def play_alert(self):
        """Play alert sound using system beep"""
        try:
            # Try using paplay (PulseAudio)
            subprocess.run(['paplay', '/usr/share/sounds/freedesktop/stereo/complete.oga'])
        except FileNotFoundError:
            # Fallback to console beep
            print('\a')
            
    def log_activity(self, event_type="Activity Update"):
        """Log activity duration to file with remaining time"""
        remaining_time = max(timedelta(), self.time_limit - self.total_active_time)
        session_duration = datetime.now() - self.start_time
        
        with open(self.log_file, 'a') as f:
            f.write(
                f"[{datetime.now()}] - {event_type}\n"
                f"  Session Duration: {self.format_timedelta(session_duration)}\n"
                f"  Total Active Time: {self.format_timedelta(self.total_active_time)}\n"
                f"  Time Limit: {self.format_timedelta(self.time_limit)}\n"
                f"  Remaining Time: {self.format_timedelta(remaining_time)}\n"
                f"  Activity Rate: {(self.total_active_time.total_seconds() / max(1, session_duration.total_seconds()) * 100):.1f}%\n"
                f"  Alerts Played: {self.alert_count}/{self.max_alerts}\n"
                f"  Status: {'Time Limit Reached' if remaining_time.total_seconds() <= 0 else 'Active'}\n"
                f"{'=' * 50}\n"
            )
            
    def start(self):
        """Start monitoring"""
        print(f"Starting input monitoring. Time limit: {self.time_limit}")
        print(f"Logging activity to: {self.log_file}")
        print("* indicates active input")
        print(f"Alert will sound {self.max_alerts} times when time limit is reached")
        print(f"Activity log updated every {self.log_interval.seconds} seconds")
        
        # Log initial state
        self.log_activity("Session Started")
        
        # Start progress bar in a separate thread
        progress_thread = threading.Thread(target=self.draw_progress_bar)
        progress_thread.daemon = True
        progress_thread.start()
        
        # Start the hook manager
        self.hook_manager.start()
        
def main():
    parser = argparse.ArgumentParser(description='Monitor input activity with time limit')
    parser.add_argument('-tm', '--time', required=True, help='Time limit in format 1h10m01s')
    
    args = parser.parse_args()
    
    try:
        time_limit = InputMonitor.parse_time_limit(args.time)
        monitor = InputMonitor(time_limit)
        monitor.start()
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
        return 0
        
if __name__ == "__main__":
    exit(main())
