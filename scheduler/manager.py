"""
Scheduler Manager for goobie-bot
Manages all scheduled tasks to prevent duplicates and handle reconnections
"""

import asyncio
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class SchedulerManager:
    """Manages all scheduled tasks to prevent duplicates and handle reconnections"""

    def __init__(self):
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_lock = asyncio.Lock()

    async def start_scheduler(self, name: str, coro, *args, **kwargs) -> bool:
        """
        Start a scheduler task if it's not already running

        Args:
            name: Unique name for the scheduler
            coro: Coroutine function to run
            *args, **kwargs: Arguments to pass to the coroutine

        Returns:
            bool: True if started, False if already running
        """
        async with self.task_lock:
            if name in self.running_tasks:
                task = self.running_tasks[name]
                if not task.done():
                    logger.info(
                        f"Scheduler '{name}' is already running, skipping start"
                    )
                    return False
                else:
                    # Task is done, remove it
                    logger.info(
                        f"Scheduler '{name}' was completed, removing from registry"
                    )
                    del self.running_tasks[name]

            # Start new task
            logger.info(f"Starting scheduler: {name}")
            task = asyncio.create_task(coro(*args, **kwargs))
            self.running_tasks[name] = task

            # Add callback to clean up when task completes
            task.add_done_callback(lambda t: self._cleanup_task(name, t))

            logger.info(f"Scheduler '{name}' started successfully")
            return True

    def _cleanup_task(self, name: str, task: asyncio.Task):
        """Clean up completed or cancelled tasks"""
        if name in self.running_tasks and self.running_tasks[name] == task:
            if task.cancelled():
                logger.info(f"Scheduler '{name}' was cancelled")
            elif task.exception():
                logger.error(
                    f"Scheduler '{name}' failed with exception: {task.exception()}"
                )
            else:
                logger.info(f"Scheduler '{name}' completed normally")

            # Remove from registry
            if name in self.running_tasks:
                del self.running_tasks[name]

    async def stop_scheduler(self, name: str) -> bool:
        """
        Stop a specific scheduler task

        Args:
            name: Name of the scheduler to stop

        Returns:
            bool: True if stopped, False if not running
        """
        async with self.task_lock:
            if name not in self.running_tasks:
                logger.info(f"Scheduler '{name}' is not running")
                return False

            task = self.running_tasks[name]
            if not task.done():
                logger.info(f"Stopping scheduler: {name}")
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                logger.info(f"Scheduler '{name}' stopped")

            # Remove from registry
            del self.running_tasks[name]
            return True

    async def stop_all_schedulers(self):
        """Stop all running scheduler tasks"""
        async with self.task_lock:
            if not self.running_tasks:
                logger.info("No schedulers running")
                return

            logger.info(f"Stopping {len(self.running_tasks)} schedulers...")

            # Cancel all tasks
            for name, task in self.running_tasks.items():
                if not task.done():
                    logger.info(f"Stopping scheduler: {name}")
                    task.cancel()

            # Wait for all tasks to complete
            if self.running_tasks:
                await asyncio.gather(
                    *self.running_tasks.values(), return_exceptions=True
                )

            # Clear registry
            self.running_tasks.clear()
            logger.info("All schedulers stopped")

    def get_running_schedulers(self) -> Dict[str, str]:
        """Get status of all running schedulers"""
        status = {}
        for name, task in self.running_tasks.items():
            if task.done():
                if task.cancelled():
                    status[name] = "cancelled"
                elif task.exception():
                    status[name] = f"failed: {task.exception()}"
                else:
                    status[name] = "completed"
            else:
                status[name] = "running"
        return status

    def is_scheduler_running(self, name: str) -> bool:
        """Check if a specific scheduler is running"""
        if name not in self.running_tasks:
            return False

        task = self.running_tasks[name]
        return not task.done()


# Global scheduler manager instance
scheduler_manager = SchedulerManager()
