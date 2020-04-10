import json
import os

import azure.functions as func
import azure.durable_functions as df

def orchestrator_function(context: df.DurableOrchestrationContext):
    """This function provides a sample for activity trigger

    Parameters
    ----------
    context: DurableOrchestrationContext
        This context has the past history and the durable orchestration API

    Returns
    -------
    message
        Returns the result of the activity function return values.

    Yields
    -------
    call_activity: str
        Yields, depending on the `json_rule`, to wait on either all
        tasks to complete, or until one of the tasks completes.
    """

    message = []

    ret_bool = yield context.call_activity("ReturnBool", "1")
    message.append(f"ret_bool: {ret_bool} {type(ret_bool)}")

    # Not supported: return value from activity trigger "bytes" is not json serializable!
    # ret_bytes = yield context.call_activity("ReturnBytes", "1b2b3b")
    # message.append(f"ret_bytes : {ret_bytes} {type(ret_bytes)}")

    ret_dict_of_string = yield context.call_activity("ReturnDictOfString", "kv")
    message.append(f"ret_dict_of_string : {ret_dict_of_string} {type(ret_dict_of_string)}")

    ret_dict_of_string_anno = yield context.call_activity("ReturnDictOfStringWithAnnotation", "kv_anno")
    message.append(f"ret_dict_of_string_anno : {ret_dict_of_string_anno} {type(ret_dict_of_string_anno)}")

    ret_float = yield context.call_activity("ReturnFloat", "123.0")
    message.append(f"ret_float : {ret_float} {type(ret_float)}")

    ret_int = yield context.call_activity("ReturnInt", "123")
    message.append(f"ret_int : {ret_int} {type(ret_int)}")

    ret_int_from_float = yield context.call_activity("ReturnIntFromFloat", 3.14)
    message.append(f"ret_int_from_float : {ret_int_from_float} {type(ret_int_from_float)}")

    ret_list_of_float = yield context.call_activity("ReturnListOfFloat", "4.5")
    message.append(f"ret_list_of_float : {ret_list_of_float} {type(ret_list_of_float)}")

    ret_list_of_float_anno = yield context.call_activity("ReturnListOfFloatWithAnnotation", "5.6")
    message.append(f"ret_list_of_float_anno : {ret_list_of_float_anno} {type(ret_list_of_float_anno)}")

    # Not supported: return value from activity trigger "set" is not json serializable!
    # ret_set_of_int = yield context.call_activity("ReturnSetOfInt", 5)
    # message.append(f"ret_set_of_int : {ret_set_of_int} {type(ret_set_of_int)}")

    ret_string = yield context.call_activity("ReturnString", "simple_string")
    message.append(f"ret_string : {ret_string} {type(ret_string)}")

    return message


main = df.Orchestrator.create(orchestrator_function)
