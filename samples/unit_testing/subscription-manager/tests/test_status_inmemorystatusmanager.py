from ..Status.inmemorystatusmanager import InMemoryStatusManager
from unittest import IsolatedAsyncioTestCase

"""
Test class for InMemoryStatusManager that tests status management
"""
class TestInMemoryStatusManager(IsolatedAsyncioTestCase):

    def update_callback(self,status):
        status.name = "test_status"
        status.creation_status = "Succeeded"
        assert status.last_updated_time != None
        return status

    async def test_get_new_status(self):
        client_name = "test"
        status_mgr : InMemoryStatusManager = InMemoryStatusManager(client_name)
        self.assertEqual(status_mgr.state_file_name,f"{client_name}.json")

        # Get the status entry
        status = await status_mgr.get_status()
        self.assertEqual(status.name,"")
    
    async def test_update_status_with_callback(self):
        client_name = "test"
        status_mgr : InMemoryStatusManager = InMemoryStatusManager(client_name)

        # create a fresh status entry
        status = await status_mgr.get_status()
        await status_mgr.safe_update_status(self.update_callback)
        updated_status = status_mgr.status_entries[status_mgr.state_file_name]

        # Check the updated status from status entries
        self.assertEqual(updated_status.name,"test_status")
        self.assertEqual(updated_status.creation_status,"Succeeded")

    
