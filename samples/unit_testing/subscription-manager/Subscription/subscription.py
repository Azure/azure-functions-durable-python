from typing import Dict
import json

class ManagementGroupParent:
    def __init__(self, id:str):
        self.id = id

class ManagementGroupMoveProperties:
    def __init__(self,display_name:str,parent:ManagementGroupParent,state:str,tenant:str):
        self.display_name = display_name
        self.parent = parent
        self.state = state
        self.tenant = tenant

class ManagementGroupMoveResponse:
    def __init__(self,mgmt_name:str,mgmt_id:str,mgmt_type:str,props: ManagementGroupMoveProperties):
        self.name = mgmt_name
        self.id = mgmt_id
        self.type = mgmt_type
        self.properties = props

class SubscriptionProperties:
    def __init__(self,subscription_id: str,provisioning_state:str):
        self.subscriptionId = subscription_id
        self.provisioningState = provisioning_state 
"""
Represents a Subscription State

from_json and to_json methods exist to enable serialization through durable python framework
"""
class SubscriptionResponse:
    def __init__(self, sub_id:str,sub_name:str,sub_type:str,sub_props: SubscriptionProperties):
        self.id = sub_id
        self.name = sub_name
        self.type = sub_type
        self.properties = sub_props

    @staticmethod
    def to_json(obj : object) -> str:
        str_obj = {
            "name" : obj.name,
            "id" : obj.id,
            "type": obj.type,
            "properties" : { "subscriptionId":obj.properties.subscriptionId,"provisioningState": obj.properties.provisioningState}
        }
        return str(str_obj)
    
    @staticmethod
    def from_json(json_str: str) -> object:
        json_str = json_str.replace("\'", "\"")
        obj_kv = json.loads(json_str)
        props : SubscriptionProperties = SubscriptionProperties(obj_kv["properties"]["subscriptionId"],obj_kv["properties"]["provisioningState"])
        sub_obj = SubscriptionResponse( obj_kv["id"],obj_kv["name"],obj_kv["type"],props)
        return sub_obj

"""
Represents Lifecycle of subscription interface
"""
class SubscriptionInterface:
    def __init__(self):
        pass

    async def get_billing_account_id(self) -> str:
        pass
    
    async def get_enrollment_account_id(self) -> str:
        pass

    async def create_subscription(self,subscription_name:str,display_name:str) -> SubscriptionResponse:
        pass

    async def get_subscription_status(self, subscription_name:str) -> SubscriptionResponse:
        pass

    async def move_subscription(self,subscription_id:str,management_group_id:str) -> ManagementGroupMoveResponse:
        pass