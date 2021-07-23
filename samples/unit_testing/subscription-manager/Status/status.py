import json
from typing import Callable,Any

"""
Status object that represents the state of subscription creation process
The from_json and to_json methods are implemented here for automatic
serialization by the Durable framework
"""
class Status(object):

    # Change to kwargs
    def __init__(self,name=None,state_id=0,last_updated_time=None,
                 pim_enabled=False,creation_status=None):
        self.name = str(name)
        self.id = str(state_id)
        self.last_updated_time = str(last_updated_time)
        self.pim_enabled = str(pim_enabled)
        self.creation_status = str(creation_status)
    
    @staticmethod
    def to_json(obj : object) -> str:
        str_obj = {
            "name" : obj.name,
            "id" : obj.id,
            "last_updated_time" : obj.last_updated_time,
            "pim_enabled" : obj.pim_enabled,
            "creation_status" : obj.creation_status
        }
        return str(str_obj)
    
    @staticmethod
    def from_json(json_str: str) -> object:
        json_str = json_str.replace("\'", "\"")
        obj_kv = json.loads(json_str)
        status_obj = Status( obj_kv["name"],obj_kv["id"],obj_kv["last_updated_time"],
                             obj_kv["pim_enabled"],obj_kv["creation_status"])
        return status_obj

"""
Status Manager Interface that can be implemented through:

get_status: retrieving status from memory/storage
safe_update_status: update status safely by acquiring lease and providing a callback to the caller to update the status further.
"""
class StatusManagerInterface:

    def __init__(self,status):
        self.status : Status = status
    
    async def get_status() -> Status:
        pass

    async def safe_update_status(update_cb: Callable[[Status],Any]):
        pass