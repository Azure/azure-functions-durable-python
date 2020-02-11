import json
import azure.durable_functions as df


def generator_function(context):
    config = {
        "instances": 5,
        "number_of_images": 15
    }
    generation_info = {"config": config, "seed": context.instance_id}
    generation_data = yield context.call_activity("GetGenerationData", json.dumps(generation_info))

    activity_list = json.loads(generation_data)

    image_data = yield context.call_activity("GetImageUrls", config['number_of_images'])

    image_count_per_instance = int(
        config['number_of_images']/config['instances'])

    image_list = json.loads(image_data)
    tasks = []

    start = 0
    increment = image_count_per_instance

    for i in activity_list:
        instance_images = image_list[start:increment]
        tasks.append(
            context.call_activity("ClassifyImage",
                                  {"instance_info": i,
                                   "images": instance_images}))
        start += image_count_per_instance
        increment += image_count_per_instance

    predictions = yield context.task_all(tasks)
    
    combined = []
    for tr in predictions:
        prediction = json.loads(tr)
        combined.extend(prediction['prediction_results'])

    message = yield context.call_activity("ShowMeTheResults", combined)

    return message


def main(context: str):
    orchestrate = df.Orchestrator.create(generator_function)

    result = orchestrate(context)

    return result
