from typing import List, Any
from ..models.actions.CreateTimerAction import CreateTimerAction
from ..models.history import HistoryEvent
from .task_utilities import \
    find_timer_created, find_timer_fired, set_processed
import datetime
from .timer_task import TimerTask

def create_timer_task(state: List[HistoryEvent],
                      fire_at: datetime) -> TimerTask:
    """
    Durable Timers are used in orchestrator functions to implement delays or to
    setup timeouts on async actions.
    
    Parameters
    ----------
    state : List[HistoryEvent]
        The list of history events to search to determine the current state of the activity
    fire_at : datetime
        The time interval to fire the timer trigger
    
    Returns
    -------
    TimerTask
        A Durable Timer Task that schedules the timer to wake up the activity
    """

    new_action = CreateTimerAction(fire_at)

    timer_created = find_timer_created(state,fire_at)
    timer_fired = find_timer_fired(state,timer_created)

    set_processed([timer_created,timer_fired])

    if timer_fired:
          return TimerTask(
            is_completed=True,
            action=new_action,
            timestamp=timer_fired["Timestamp"],
            id_=timer_fired["TaskScheduledId"])
    else:
          return TimerTask(
            is_completed=False,
            action=new_action,
            timestamp=None,
            id_=None)

   