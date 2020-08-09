class EntityId:
    @staticmethod
    def get_scheduler_id(entity_id: EntityId) -> str:
        return f"@{entity_id.name.lower()}@{entity_id.key}"

    @staticmethod
    def get_entity_id(scheduler_id: str) -> EntityId:
        sched_id_truncated = scheduler_id[1:] # we drop the starting `@`
        components = sched_id_truncated.split("@")
        if len(components) > 2:
            raise ValueError("Unexpected format in SchedulerId")
        [name, key] = components
        return EntityId(name, key)
    
    def __init__(self, name: str, key: str):
        if name == "":
            raise ValueError("Entity name cannot be empty")
        if key == "":
            raise ValueError("Entity key cannot be empty")
        self.name: str = name
        self.key: str = key
    
    def __str__(self):
        return EntityId.get_scheduler_id(entity_id=self)