# backend/sandbox_engine.py
import docker
import tarfile
import io

# backend/sandbox_engine.py

# The ULTIMATE Polyglot Execution Configuration
LANGUAGE_CONFIG = {
    "python": {
        "image": "python:3.11-slim",
        "ext": ".py",
        "command": "timeout 10 python script.py"
    },
    "javascript": {
        "image": "node:20-alpine",
        "ext": ".js",
        "command": "timeout 10 node script.js"
    },
    "c": {
        "image": "gcc:latest",
        "ext": ".c",
        "command": "timeout 15 sh -c 'gcc script.c -o out_bin && ./out_bin'"
    },
    "cpp": {
        "image": "gcc:latest",
        "ext": ".cpp",
        "command": "timeout 15 sh -c 'g++ script.cpp -o out_bin && ./out_bin'"
    },
    "rust": {
        "image": "rust:alpine",
        "ext": ".rs",
        "command": "timeout 15 sh -c 'rustc script.rs -o out_bin && ./out_bin'"
    },
    "go": {
        "image": "golang:alpine",
        "ext": ".go",
        "command": "timeout 10 go run script.go"
    },
    "java": {
        "image": "openjdk:21-jdk-slim",
        "ext": ".java",
        "command": "timeout 15 sh -c 'mv script.java Main.java && javac Main.java && java Main'"
    }
}

class UltraSandbox:
    def __init__(self):
        self.client = docker.from_env()

    def start(self):
        """
        We now use Ephemeral Containers per-run to support multiple languages seamlessly.
        This dummy method keeps your agent_brain.py from breaking.
        """
        print("📦 Polyglot Sandbox initialized. Containers will spin up on demand.")
        return "polyglot-sandbox-ready"

    def run_code(self, code: str, dataset: str = None, language: str = "python"):
        # 1. Route to the correct language config
        config = LANGUAGE_CONFIG.get(language.lower(), LANGUAGE_CONFIG["python"])
        filename = f"script{config['ext']}"

        # 2. Package the code (and optional dataset) into a TAR archive
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            data = code.encode('utf-8')
            info = tarfile.TarInfo(name=filename)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
            
            if dataset:
                ds_data = dataset.encode('utf-8')
                ds_info = tarfile.TarInfo(name="data.csv")
                ds_info.size = len(ds_data)
                tar.addfile(ds_info, io.BytesIO(ds_data))
                
        tar_stream.seek(0)

        print(f"🐳 Spinning up Ephemeral {config['image']} container for {language}...")
        
        try:
            # 3. Spin up the specific container for this language
            container = self.client.containers.run(
                config["image"],
                command="tail -f /dev/null", # Keep alive to inject code
                detach=True,
                mem_limit="512m",
                network_disabled=False, 
                working_dir="/app"
            )
            
            # If it's Python, quickly provision standard data libraries
            if language.lower() == "python":
                container.exec_run("pip install pandas requests beautifulsoup4")
            
            # 4. Inject the code and execute
            container.put_archive("/app", tar_stream)
            exec_result = container.exec_run(config["command"])
            
            # 5. Cleanup: Destroy the sandbox immediately after execution
            container.remove(force=True)

            if exec_result.exit_code == 124:
                return {"exit_code": 124, "output": f"TimeoutError: {language} execution took too long (>10s)."}
                
            return {
                "exit_code": exec_result.exit_code,
                "output": exec_result.output.decode("utf-8")
            }
            
        except Exception as e:
            return {"exit_code": 1, "output": f"Docker Sandbox Error: {str(e)}"}

    def stop(self):
        """Ephemeral containers are destroyed automatically in run_code."""
        pass