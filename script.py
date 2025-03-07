import time
import threading
from datetime import datetime, timedelta

scheduled_tasks = []
scheduler_thread = None
running = True

def schedule_reminder(title, message, timeout):
    task = {
        "title": title,
        "message": message,
        "timeout_seconds": timeout,
        "next_run": datetime.now() + timedelta(seconds=timeout),
        "active": True
    }
    scheduled_tasks.append(task)
    print(f"Reminder scheduled to send once in {timeout} seconds.")

def start_scheduler():
    global scheduler_thread
    print("Starting scheduler...")
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("Scheduler is now running.")

def run_scheduler():
    global running
    while running:
        for task in list(scheduled_tasks):  # Create a copy of the list to safely modify during iteration
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
    print(f"NOTIFICATION: {task['title']} - {task['message']}")
    # No longer removing tasks or updating next_run as each task runs only once

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
        print(f"{task['title']}: {time_remaining(task):.1f} seconds remaining")

def main():
    # Start scheduler at startup
    start_scheduler()
    
    while True:
        print("\n1. Schedule Reminder")
        print("2. View Scheduled Tasks")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
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
        elif choice == "2":
            display_scheduled_tasks()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()