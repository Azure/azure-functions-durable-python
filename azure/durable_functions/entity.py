from models.entities import DurableEntityContext

class Entity:
    def __init__(self, entity_func):
        self.fn = entity_func
    
    def handle(self, context):
        raise ValueError("We did it!")
        """
        .....
        return_state = ...
        returnState.entity_exists = ...
        return_state.entiy_state = ...
        for(.............):
            context ?
            try:
                # TODO: maybe move elapsed millis gen to the constructor of
                # OperationResult
                elapsed_millis = _elapsed_milliseconds_since(start_time)
                operation_result =OperationResult(
                    is_error=False,
                    duration=elapsed_millis,
                    result=......

                )
                ...
            except Exception as e:
                elapsed_millis = _elapsed_milliseconds_since(start_time)  
                operation_result = OperationResult(
                    is_error=True,
                    duration=elapsed_millis,
                    result=str(e)
                )
                return_state.results.append(operation_result)
        return entity_state.to_json_string()
        """
        return None




    @classmethod
    def create(cls, fn):
        def handle_(context) -> str:
            # TODO: this requires some commenting, where do we need to get this from the body
            context_body = getattr(context, "body", None)
            if context_body is None:
                context_body = context
            return Entity(fn).handle(DurableEntityContext.from_json(context_body))
    return handle_