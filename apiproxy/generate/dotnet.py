from typing import List
from ..service.models import GeneratedFile, Traffic


async def generate_asp_net_api(traffic: Traffic) -> List[GeneratedFile]:
    files: List[GeneratedFile] = []

    controller = """
        """

    files.append(
        GeneratedFile(file_name="Controllers/Controller.cs", content=controller)
    )

    return files
