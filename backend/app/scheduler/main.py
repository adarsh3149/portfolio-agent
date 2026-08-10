import time

from app.scheduler.bootstrap import create_scheduler


def start_scheduler():
    scheduler = create_scheduler()

    scheduler.start()

    return scheduler


def run_scheduler():
    scheduler = start_scheduler()

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    run_scheduler()