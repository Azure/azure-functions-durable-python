import json
from typing import List
import azure.functions as func
import azure.durable_functions as df


def _get_classify_images_tasks(config: dict, image_list: List[str], context: df.DurableOrchestrationContext):
    """Get list of tasks that breaks down the execution of the predications.

    will create a list of tasks to perform that is split evenly across the
    different instances

    Parameters
    ----------
    config: dict
        Describes how the tasks will be split
    image_list: List[str]
        The list of images to classify
    context: df.DurableOrchestrationContext
        The Durable context to call the activities from

    Returns
    -------
    tasks: List
        List of tasks to perform
    """
    image_count_per_instance = int(
        config['number_of_images']/config['instances'])

    tasks = []

    start = 0
    increment = image_count_per_instance

    for _ in range(config['instances']):
        instance_images = image_list[start:increment]
        tasks.append(
            context.call_activity("ClassifyImage",
                                  instance_images))
        start += image_count_per_instance
        increment += image_count_per_instance

    return tasks


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Get the generator that will need to be orchestrated by durable functions.

    This function will get a list of images to do a prediction of, fan out the
    prediction tasks then summarize the results

    Parameters
    ----------
    context: df.DurableOrchestrationContext
        The Durable context to perform the activities with

    Returns
    -------
    summary
        A summary of the prediction results

    Yields
    -------
        Tasks that need to be performed by the Durable orchestrator
    """
    config = {
        "instances": 5,  # The number of instances to fan out the prediction tasks
        "number_of_images": 15  # The number of images to predict
    }

    # Get the images that need to predicted
    image_data = yield context.call_activity("GetImageUrls", config['number_of_images'])
    image_list = json.loads(image_data)

    # break the images done into different tasks to be fan out with
    tasks = _get_classify_images_tasks(config, image_list, context)
    predictions = yield context.task_all(tasks)

    # combine the results of the predictions into a single list
    combined = []
    for tr in predictions:
        prediction = json.loads(tr)
        combined.extend(prediction)

    # summarize the results
    summary = yield context.call_activity("ShowMeTheResults", combined)
    return summary


main = df.Orchestrator.create(orchestrator_function)
