from typing import List
from .java_model import GeneratedFile, generate_java_model
from .modeler import Modeler
from .naming import guess_entity_name, pascal_case
from ..service.models import Traffic
from ..service.str_util import trim_indent, split_path


async def generate_spring_boot_server_web_mvc(traffic: Traffic) -> List[GeneratedFile]:
    entity_name = guess_entity_name(traffic.method, traffic.url)
    files: List[GeneratedFile] = []

    modeler = Modeler()

    if traffic.req_body:
        request_class = pascal_case(entity_name) + "Request"
        parameters = f"@RequestBody {request_class} request"
        modeler.analyze(traffic.req_body, request_class)

    else:
        request_class = None
        parameters = ""

    if traffic.resp_body:
        response_class = "Response"
        modeler.analyze(traffic.resp_body, response_class)

    for class_def in modeler.get_classes():
        files.append(generate_java_model(class_def))

    method = traffic.method
    base_path, method_path = split_path(traffic.url)
    entity_name = guess_entity_name(method, method_path)

    if method == "GET":
        method_annotation = f'@GetMapping("{method_path}")'
    elif method == "POST":
        method_annotation = f'@PostMapping(value = "{method_path}")'
    elif method == "PUT":
        method_annotation = f'@PutMapping(value = "{method_path}")'
    elif method == "DELETE":
        method_annotation = f'@DeleteMapping(value = "{method_path}")'
    else:
        method_annotation = (
            f'@RequestMapping(method = RequestMethod.{method}, path = "{method_path}")'
        )

    if traffic.resp_body:
        response_class = pascal_case(entity_name) + "Response"
    else:
        response_class = "String"

    controller = trim_indent(
        f"""
        import org.slf4j.Logger;
        import org.slf4j.LoggerFactory;
        import org.springframework.beans.factory.annotation.Autowired;
        import org.springframework.web.bind.annotation.PostMapping;
        import org.springframework.web.bind.annotation.RequestBody;
        import org.springframework.web.bind.annotation.RequestMapping;
        import org.springframework.web.bind.annotation.RestController;

        @RestController
        @RequestMapping("{base_path}")
        public class ApiController {{
            
            {method_annotation}
            public ResponseEntity<{response_class}> handleRequest({parameters}) {{

                ResponseEntity<{response_class}> response = new ResponseEntity();
                return response;
            }}
        }}
        """
    )

    files.append(GeneratedFile(file_name="web/ApiController.java", content=controller))
    return files


async def generate_spring_boot_server_web_flux(traffic: Traffic) -> str:
    return """import org.springframework.http.HttpHeaders;
        import org.springframework.http.HttpMethod;
        import org.springframework.http.ResponseEntity; 
        import org.springframework.web.reactive.function.client.WebClient;
        """
