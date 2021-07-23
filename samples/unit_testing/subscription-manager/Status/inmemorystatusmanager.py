from ..Status.status import StatusManagerInterface, Status
from typing import Dict,Callable,Any
import datetime

"""
In Memory implementation of status manager interface for local and unit testing
Retrieves and updates Status of a subscription in memory
"""
class InMemoryStatusManager(StatusManagerInterface):
    status_entries: Dict[str,Status] = {}

    def __init__(self,client_name):
        self.client_name: str = client_name
        self.state_file_name: str = f"{self.client_name}.json"
    
    async def get_status(self) -> Status:
        if self.state_file_name not in self.status_entries:
            self.status_entries[self.state_file_name] = Status("")
        return self.status_entries[self.state_file_name]
        
    async def safe_update_status(self,update_cb: Callable[[Status],Any]):
        target_status = await self.get_status()
        if target_status:
            now = datetime.datetime.now()
            target_status.last_updated_time = datetime.datetime.strftime(now,'%Y-%m-%d %H:%M')
            updated_status = update_cb(target_status)
            self.status_entries[self.state_file_name] = updated_status