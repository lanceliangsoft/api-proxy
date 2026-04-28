import json
from re import I
from typing import Any, List

from .naming import camel_case, guess_entity_name
from .modeler import ClassDef, ListDef, Modeler, ValueType, pascal_case
from ..service.models import GeneratedFile, Traffic
from ..service.str_util import indent, quote_string, split_path, split_url, trim_indent


def get_cs_type(type: ValueType) -> str:
    if isinstance(type, ClassDef):
        return type.name
    elif isinstance(type, ListDef):
        return "List<" + get_cs_type(type.elem_type) + ">"
    elif type == "String":
        return "string"
    elif type == "int":
        return "int"
    elif type == "double":
        return "double"
    elif type == "None":
        return "Object"
    elif type == "Object":
        return "Object"
    else:
        print(f"get_cs_type({type})")
        return str(type)


def generate_cs_model(class_def: ClassDef) -> GeneratedFile:
    content = trim_indent(f"""
        namespace Models;
                          
        public class {class_def.name}
        """)
    content += "{\n"
    for field in class_def.fields:
        content += f'    [JsonPropertyName("{field.name}")]\n'
        content += f"    public {get_cs_type(field.type)}? {pascal_case(field.name)} {{ get; set; }}\n\n"
    content += "}\n"

    return GeneratedFile(file_name=f"Models/{class_def.name}.cs", content=content)


def generate_cs_value(value: Any, type: ValueType, indent: int) -> str:
    if isinstance(type, ClassDef):
        return generate_cs_data_init(type, value, indent)  # type: ignore
    elif isinstance(type, ListDef):
        first = True
        desc = "["
        for item in value:
            if first:
                first = False
            else:
                desc += ","
            desc += (
                "\n"
                + (" " * (indent + 4))
                + generate_cs_value(item, type.elem_type, indent + 4)
            )
        desc += "\n" + (" " * indent) + "]"
        return desc
    elif type == "String":
        return quote_string(value)
    elif type == "int":
        return str(value)
    elif type == "double":
        return str(value)
    elif type == "None":
        return "null"
    else:
        return str(value)


def generate_cs_data_init(class_def: ClassDef, data: dict, indent: int) -> str:
    type_name = get_cs_type(class_def)

    desc = f"new {type_name}\n" + (" " * indent) + "{"
    first = True
    for field in class_def.fields:
        if first:
            first = False
        else:
            desc += ","
        desc += (
            "\n"
            + (" " * (indent + 4))
            + f"{pascal_case(field.name)}="
            + generate_cs_value(data.get(field.name), field.type, indent + 4)
        )

    desc += "\n" + (" " * indent) + "}"
    return desc


async def generate_cs_models(json_payload: str, root_element: str) -> List[GeneratedFile]:
    files: List[GeneratedFile] = []
    modeler = Modeler()

    modeler.analyze(
        json_payload.encode(), root_element
    )
    for class_def in modeler.get_classes():
        files.append(generate_cs_model(class_def))
    return files


async def generate_asp_net_api(traffic: Traffic) -> List[GeneratedFile]:
    op_name = pascal_case(guess_entity_name(traffic.method, traffic.url))
    service_name = "ExampleService"

    files: List[GeneratedFile] = []
    modeler = Modeler()

    if traffic.req_body:
        request_class = modeler.analyze(
            traffic.req_body, pascal_case(op_name) + "Request"
        )
        request_class_name = get_cs_type(request_class)
        parameters = f"{request_class_name} request"
        parameter_vars = "request"

    else:
        request_class = None
        request_class_name = None
        parameters = ""
        parameter_vars = ""

    if traffic.resp_body:
        response_class = modeler.analyze(
            traffic.resp_body, pascal_case(op_name) + "Response"
        )
        response_class_name = get_cs_type(response_class)
    else:
        response_class = None
        response_class_name = "Object"

    for class_def in modeler.get_classes():
        files.append(generate_cs_model(class_def))

    method = traffic.method
    base_path, method_path = split_path(traffic.url)
    op_name = guess_entity_name(method, method_path)

    if method == "GET":
        method_annotation = f'[HttpGet("{method_path}")]'
    elif method == "POST":
        method_annotation = f'[HttpPost("{method_path}")]'
    elif method == "PUT":
        method_annotation = f'[HttpPut("{method_path}")]'
    elif method == "DELETE":
        method_annotation = f'[HttpDelete("{method_path}")]'
    elif method == "PATCH":
        method_annotation = f'[HttpPatch("{method_path}")]'
    else:
        return files

    if traffic.resp_body:
        init_data = json.loads(traffic.resp_body.decode())

        service_impl = trim_indent(f"""
            using Models;
                                
            namespace Services;
                                
            public class {service_name}
            {{
                public async {response_class_name} {op_name}({parameters})
                {{
                    return {indent(20, generate_cs_data_init(response_class, init_data))}
                }}
            }}
            """)

        files.append(
            GeneratedFile(file_name="Services/Controller.cs", content=service_impl)
        )
    else:
        response_class_name = "Object"

    controller = trim_indent(f"""
        using Microsoft.AspNetCore.Mvc;
        using Models;
        using Services;
        
        namespace Controllers;
                             
        [ApiController]
        [Route("[controller]")]
        public class ExampleController : ControllerBase
        {{
            private {service_name} {camel_case(service_name)};

            public ExampleController({service_name} {camel_case(service_name)})
            {{
                this.{camel_case(service_name)} = {camel_case(service_name)};
            }}

            {method_annotation}
            public async {response_class_name} {op_name}({parameters})
            {{
                var response = await {service_name}.{op_name}({parameter_vars});

                return response;
            }}
        }}
        """)

    files.append(
        GeneratedFile(file_name="Controllers/Controller.cs", content=controller)
    )

    return files


async def generate_dot_net_client(traffic: Traffic) -> List[GeneratedFile]:
    op_name = pascal_case(guess_entity_name(traffic.method, traffic.url))

    files: List[GeneratedFile] = []
    modeler = Modeler()

    if traffic.req_body:
        request_class = modeler.analyze(
            traffic.req_body, pascal_case(op_name) + "Request"
        )
        request_class_name = get_cs_type(request_class)
        parameters = f"{request_class_name} request"
    else:
        request_class = None
        request_class_name = None
        parameters = ""

    if traffic.resp_body:
        response_class = modeler.analyze(
            traffic.resp_body, pascal_case(op_name) + "Response"
        )
        response_class_name = get_cs_type(response_class)
    else:
        response_class = None
        response_class_name = "Object"

    for class_def in modeler.get_classes():
        files.append(generate_cs_model(class_def))

    if traffic.req_body is not None and request_class is not None:
        req_obj = json.loads(traffic.req_body.decode())

        example_call = trim_indent(
            f"""public async Task<{response_class_name}?> {op_name}Example()
            {{
                var request = {generate_cs_value(req_obj, request_class, 16)};
                return await {op_name}(request);
            }}"""
        )
    else:
        example_call = ""

    client_code = trim_indent(f"""
        using System.Reflection;
        using System.Text;
        using System.Text.Json;
        using System.Text.Json.Serialization;
        using Models;
        
        namespace Clients;
                             
        public class ExampleClient
        {{
            private ILogger _logger;
                             
            public ExampleClient(ILoggerFactory logFactory)
            {{
                this._logger = logFactory.CreateLogger(Assembly.GetExecutingAssembly().GetName().Name);         
            }}

            public async Task<{response_class_name}?> {op_name}({parameters})
            {{
                try
                {{
                    HttpClient client = new HttpClient();
    
                    var response = await client.PostAsJsonAsync("{traffic.url}", request);
                    string responseContent = await response.Content.ReadAsStringAsync();
                    return JsonSerializer.Deserialize<{response_class_name}>(responseContent);
                }}
                catch (Exception e)
                {{
                    _logger.LogError("Fail to call REST api {{}}", e);
                    return null;
                }}
            }}

            {indent(12, example_call)}
        }}
        """)

    files.append(
        GeneratedFile(file_name="Clients/ExampleClient.cs", content=client_code)
    )
    return files
