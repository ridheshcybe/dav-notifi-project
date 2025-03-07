import time
import platform
import subprocess
import threading
from datetime import datetime, timedelta

scheduled_tasks = []
scheduler_thread = None
running = False

def schedule_reminder(title, message, timeout):
    task = {
        "func": send_notification,
        "args": (title, message),
        "timeout_seconds": timeout,
        "next_run": datetime.now() + timedelta(seconds=timeout),
        "title": title,
        "message": message,
        "active": True
    }
    scheduled_tasks.append(task)
    print(f"Reminder scheduled to send once in {timeout} seconds.")
    
    if not running:
        start_scheduler()


def start_scheduler():
    global running, scheduler_thread
    if running:
        print("Scheduler is already running.")
        return
    print("Starting scheduler...")
    running = True
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("Scheduler is now running.")


def stop_scheduler():
    global running
    if not running:
        print("Scheduler is not running.")
    else:
        print("Stopping scheduler...")
        running = False
        if scheduler_thread:
            scheduler_thread.join()
        print("Scheduler stopped.")


def run_scheduler():
    global running
    while running:
        for task in scheduled_tasks:
            if should_run(task):
                run_task(task)
                scheduled_tasks.remove(task)
        time.sleep(1)


def should_run(task):
    current_time = datetime.now()
    next_run_time = task["next_run"]
    is_active = task["active"]
    
    if current_time >= next_run_time and is_active:
        return True
    else:
        return False

def run_task(task):
    send_notification(task["title"], task["message"])
    task["next_run"] = datetime.now() + timedelta(seconds=task["timeout_seconds"])

def time_remaining(task):
    if not task["active"]:
        return "Inactive"
    time_diff = task["next_run"] - datetime.now()
    return max(0, time_diff.total_seconds())


def display_scheduled_tasks():
    if not scheduled_tasks:
        print("No scheduled notifications.")
        return
    print("\nScheduled Tasks:")
    for task in scheduled_tasks:
        print(f"{task['title']}: {time_remaining(task)} seconds remaining")


def send_notification(title, message):
    system = platform.system()
    if system == "Windows":
        script = f'''
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

        $template = @"
        <toast>
            <visual>
                <binding template="ToastGeneric">
                    <text>{title}</text>
                    <text>{message}</text>
                </binding>
            </visual>
        </toast>
        "@

        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Python Script").Show($toast)'''
        subprocess.run(["powershell", "-Command", script], capture_output=True)
    elif system == "Darwin":
        subprocess.run(["osascript", "-e", f'display notification "{message}" with title "{title}"'])
    else:
        print(f"Notification: {title} - {message}")


def main():
    while True:
        print("\n1. Send Notification")
        print("2. Schedule Reminder")
        print("3. Start Scheduler")
        print("4. Stop Scheduler")
        print("5. View Scheduled Tasks")
        print("6. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            title = input("Title: ")
            message = input("Message: ")
            send_notification(title, message)
        elif choice == "2":
            title = input("Title: ")
            message = input("Message: ")
            print("\n1. 1 hour\n2. 30 minutes\n3. 1 minute\n4. 10 seconds")
            interval = input("Choose interval: ")

            # Convert interval choice to seconds (timeout)
            if interval == "1":
                timeout = 3600  # 1 hour
            elif interval == "2":
                timeout = 1800  # 30 minutes
            elif interval == "3":
                timeout = 60  # 1 minute
            elif interval == "4":
                timeout = 10  # 10 seconds
            else:
                print("Invalid choice")
                continue

            schedule_reminder(title, message, timeout)
        elif choice == "3":
            start_scheduler()
        elif choice == "4":
            stop_scheduler()
        elif choice == "5":
            display_scheduled_tasks()
        elif choice == "6":
            stop_scheduler()
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

main()