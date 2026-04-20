import os
from apiproxy.service.certmgr import make_self_signed_certificate


if __name__ == "__main__":
    make_self_signed_certificate(
        cn="localhost",
        alt_domains=[".openai.com", ".google.com", ".microsoft.com"],
        output_dir=os.path.expanduser("~/.apiproxy/certs"),
    )
