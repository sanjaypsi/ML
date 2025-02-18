import time
import numpy as np
import cv2
import pyautogui
import os
import getpass
import socket
from pynput import mouse, keyboard
from datetime import datetime, timedelta
import threading
from skimage.metrics import structural_similarity as ssim

import connect_to_db
import SystemTray

class InactivityDetector:
    def __init__(self,
                 total_runtime=3600,
                 timeout=10,
                 check_interval=5,
                 region=None):
        """
        Initializes the InactivityDetector object.

        Parameters:
        - total_runtime (int): Total runtime of the inactivity detector in seconds. Default is 3600 seconds.
        - timeout (int): Timeout duration in seconds. Default is 10 seconds.
        - check_interval (int): Interval between activity checks in seconds. Default is 5 seconds.
        - region (tuple): Region of the screen to monitor for activity. Default is None, which monitors 10% of the screen.

        Returns:
        None
        """
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.db = connect_to_db.MongoDatabase()
        print(f"Connected to MongoDB: {self.db}")

        self.total_runtime = total_runtime
        self.timeout = timeout
        self.check_interval = check_interval

        self.update_screen_resolution()
        self.region = region if region else (
            int(self.screen_width * 0.1),
            int(self.screen_height * 0.1),
            int(self.screen_width * 0.5),
            int(self.screen_height * 0.5)
        )

        self.last_activity_time = time.time()
        self.active = True
        self.start_time = time.time()
        self.active_time = 0
        self.inactive_time = 0
        self.last_check_time = self.start_time
        self.last_screenshot = None
        self.running = True

        self.mouse_listener = mouse.Listener(
            on_move=self.on_activity,
            on_click=self.on_activity,
            on_scroll=self.on_activity
        )
        self.keyboard_listener = keyboard.Listener(on_press=self.on_activity)
        self.tray_icon = SystemTray.ActivityTrayIcon(self)

    def update_screen_resolution(self):
        """
        Updates the screen resolution by retrieving the width and height of the screen.

        Returns:
            None
        """
        self.screen_width, self.screen_height = pyautogui.size()

    def start_monitoring(self):
        """
        Starts the monitoring process by creating a new thread and running the monitor method.
        """
        monitor_thread = threading.Thread(target=self.monitor)
        monitor_thread.start()

        self.tray_icon.run()

    def on_activity(self, *args):
        """
        Handles the event when user activity is detected.

        Args:
            *args: Variable number of arguments.

        Returns:
            None
        """
        if not self.active:
            print(f"{datetime.now()} - User is active again.")
        self.active = True
        self.last_activity_time = time.time()

    def take_screenshot(self):
        """
        Takes a screenshot of the specified region and returns a resized version of it.

        Returns:
            PIL.Image.Image: The resized screenshot image.
        
        Raises:
            Exception: If an error occurs while taking the screenshot.
        """
        try:
            self.update_screen_resolution()  # Ensure screen resolution is up to date
            left, top, width, height = self.region
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            return screenshot.resize((800, 600))
        except Exception as e:
            print(f"Screenshot Error: {e}")
            return None

    def compare_screenshots(self, img1, img2, threshold=0.95):
        """
        Compare two screenshots and calculate the motion intensity.

        Parameters:
        img1 (numpy.ndarray): The first screenshot image.
        img2 (numpy.ndarray): The second screenshot image.
        threshold (float, optional): The threshold value for the similarity score. Defaults to 0.95.

        Returns:
        tuple: A tuple containing two values:
            - A boolean indicating if the screenshots are similar (True) or different (False).
            - The motion intensity as a percentage.
        """
        if img1 is None or img2 is None:
            return True, 0

        img1_gray = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2GRAY)
        img2_gray = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2GRAY)

        score, diff = ssim(img1_gray, img2_gray, full=True)
        diff = (diff * 255).astype("uint8")

        _, thresh = cv2.threshold(diff, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_area = sum(cv2.contourArea(cnt) for cnt in contours)
        total_area = img1_gray.shape[0] * img1_gray.shape[1]
        motion_intensity = (motion_area / total_area) * 100

        return score < threshold, motion_intensity

    def is_user_active(self):
        """
        Checks if the user is active.

        Returns:
            bool: True if the user is active, False otherwise.
        """
        if os.name == "nt":
            sessions = os.popen("query session").read()
            return self.username in sessions and "Active" in sessions
        else:
            return self.username in os.popen("who").read()

    def log_activity(self, status, motion_intensity):
        """
        Logs the activity with the given status and motion intensity.

        Args:
            status (str): The status of the activity.
            motion_intensity (float): The intensity of the motion.

        Returns:
            None
            
        """
        # Create a log entry and insert it into the database
        pulse = {
            "username"          : self.username,
            "hostname"          : self.hostname,
            "timestamp"         : datetime.now(),
            "status"            : status,
            # "motion_intensity"  : motion_intensity,
            "active_time"       : self.active_time,
            "inactive_time"     : self.inactive_time
        }
        try:
            self.db.insert_logs(pulse)
        except Exception as e:
            print(f"Database Error: {e}")


    def monitor(self):
        """
        Monitors user activity and logs the activity status.

        This method starts the mouse and keyboard listeners and continuously checks for user activity.
        If the user is inactive for a certain period of time, it pauses the monitoring until the user becomes active again.
        It takes screenshots, compares them for motion detection, and logs the activity status and motion intensity.

        Returns:
            None
        """
        self.mouse_listener.start()
        self.keyboard_listener.start()

        try:
            while time.time() - self.start_time < self.total_runtime and self.running:
                # Call the function to print the time every minute
                if not self.is_user_active():
                    print(f"{datetime.now()} - {self.username} session inactive. Pausing...")
                    while not self.is_user_active():
                        time.sleep(self.check_interval)
                    print(f"{datetime.now()} - {self.username} session active. Resuming...")
                    self.last_activity_time = time.time()

                time_since_last_activity = time.time() - self.last_activity_time
                new_screenshot = self.take_screenshot()
                motion_detected, motion_intensity = self.compare_screenshots(self.last_screenshot, new_screenshot)
                self.last_screenshot = new_screenshot

                if motion_detected:
                    self.on_activity()

                elapsed = time.time() - self.last_check_time
                self.last_check_time = time.time()

                if time_since_last_activity <= self.timeout:
                    self.active_time += elapsed
                    self.active = True
                    status = "Active"
                else:
                    self.inactive_time += elapsed
                    self.active = False
                    status = "Inactive"

                # create a log entry and insert it into the database very 10 minutes
                if int(time.time() - self.start_time) % 300 == 0:
                    self.log_activity(status, motion_intensity)
                    print(f"{datetime.now()} - User is {status} (Motion: {motion_intensity:.2f}%)")

                # print(f"{datetime.now()} - User is {status} (Motion: {motion_intensity:.2f}%)")
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("Stopping inactivity detector.")
        finally:
            self.mouse_listener.stop()
            self.keyboard_listener.stop()
            self.print_final_summary()

    def print_final_summary(self):
        """
        Prints the final summary of the tracked time, including total time tracked, active time, and inactive time.
        Also inserts the summary into the database.

        Returns:
            None
        """
        total_time = self.active_time + self.inactive_time
        if total_time > self.total_runtime:
            self.active_time = (self.active_time / total_time) * self.total_runtime
            self.inactive_time = self.total_runtime - self.active_time
        elif total_time < self.total_runtime:
            self.inactive_time += self.total_runtime - total_time

        print(f"\nSummary:\nTotal Time Tracked: {timedelta(seconds=int(self.total_runtime))}\n"
              f"Active Time: {timedelta(seconds=int(self.active_time))} ({(self.active_time / self.total_runtime) * 100:.2f}%)\n"
              f"Inactive Time: {timedelta(seconds=int(self.inactive_time))} ({(self.inactive_time / self.total_runtime) * 100:.2f}%)\n")

        # Insert summary into database if available and handle any exceptions that may occur during insertion total_runtime 
        summary = {
            "username": self.username,
            "hostname": self.hostname,
            "session_end": datetime.now(),
            "total_runtime": self.total_runtime,
            "active_time": self.active_time,
            "inactive_time": self.inactive_time,
            "active_duration": str(timedelta(seconds=int(self.active_time))),
            "inactive_duration": str(timedelta(seconds=int(self.inactive_time)))
        }
        try:
            self.db.insert_summary(summary)
        except Exception as e:
            print(f"Database Error: {e}")

if __name__ == "__main__":
    detector = InactivityDetector(
        total_runtime   =1800,
        timeout         =300,
        check_interval  =10
    )
    detector.start_monitoring()
