from .utils.indices import index_to_schema


async def create_index(es_client):
    """Create indices for testing purposes.
    
    """
    for index in ("genres", "persons"):
        data_create_index = {
            "index": index,
            "ignore": 400,
            "body": index_to_schema.get(index)
        }
        await es_client.indices.create(
            **data_create_index
        )
