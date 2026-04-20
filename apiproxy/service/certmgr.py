from typing import List
import tempfile
import os
from .str_util import trim_indent


def make_self_signed_certificate(cn: str, alt_domains: List[str], output_dir: str):
    san_file = tempfile.TemporaryFile(
        prefix="san", suffix=".cnf", delete_on_close=False
    )
    san_file.close()
    
    print(f"san file={san_file.name}")
    desc = trim_indent(f"""[req]
        default_bits      = 2048
        distinguished_name= req_distinguished_name
        req_extensions    = v3_req
        prompt            = no
        
        [req_distinguished_name]
        C  = US
        ST = New York
        L  = New York
        O  = Development
        OU = IT
        CN = {cn}

        [v3_req]
        keyUsage = keyEncipherment, dataEncipherment
        extendedKeyUsage = serverAuth
        subjectAltName = @alt_names

        [alt_names]
        {'\n'.join([f'DNS.{index + 1} = {domain}' for index, domain in enumerate(alt_domains)])}
        IP.1 = 127.0.0.1
        """)
    
    with open(san_file.name, 'w') as f:
        f.write(desc)

    os.system(f"type {san_file.name}")
    os.makedirs(output_dir, exist_ok=True)

    command = trim_indent(
        "openssl req -x509 -nodes -days 365 -newkey rsa:2048 "
        f"-keyout {output_dir}\\server.key -out {output_dir}\\server.crt "
        f"-config {san_file.name} -extensions v3_req")
    print(command)
    os.system(command)

    os.remove(san_file.name)
