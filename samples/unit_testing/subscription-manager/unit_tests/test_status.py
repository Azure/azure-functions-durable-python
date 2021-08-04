from ..Status.status import Status
from unittest import TestCase

"""
Simple unit tests to make sure serialization methods work properly
as the custom implementations are internally used by the durable python framework
"""
class TestStatus(TestCase):
    def test_status_to_json(self):
        
        my_obj = Status("test","Microsoft/test",
                        "2021-07-19 13:11:42.477660",False,"Succeeded")
        
        str_status = Status.to_json(my_obj)
        self.assertEqual(str_status,"{'name': 'test', 'id': 'Microsoft/test', 'last_updated_time': '2021-07-19 13:11:42.477660', 'pim_enabled': 'False', 'creation_status': 'Succeeded'}")
    
    def test_status_from_json(self):

        status_obj_str = "{'name': 'test', 'id': 'Microsoft/test', 'last_updated_time': '2021-07-19 13:11:42.477660', 'pim_enabled': 'False', 'creation_status': 'Succeeded'}"
        status_obj = Status.from_json(status_obj_str)
        self.assertEqual(status_obj.name,"test")
        self.assertEqual(status_obj.id, "Microsoft/test")
        self.assertEqual(status_obj.last_updated_time,"2021-07-19 13:11:42.477660")
        self.assertEqual(status_obj.pim_enabled, "False")
        self.assertEqual(status_obj.creation_status,"Succeeded")