import docker
import tarfile
import io

class UltraSandbox:
    def __init__(self, image="python:3.9-slim"):
        self.client = docker.from_env()
        self.image = image
        self.container = None

    def start(self):
        """Starts a secure, isolated container and provisions scraping tools."""
        try:
            self.container = self.client.containers.run(
                self.image,
                command="tail -f /dev/null", 
                detach=True,
                mem_limit="512m",
                network_disabled=False, 
                working_dir="/app"
            )
            
            # Provisioning libraries for Data Analysis and Web Scraping
            print("📦 Provisioning Environment (pandas, requests, bs4)...")
            # Combined install for speed
            self.container.exec_run("pip install pandas requests beautifulsoup4")
            print("📦 Provisioning Complete! Internet-enabled sandbox ready.")
            
            return self.container.id
        except Exception as e:
            print(f"Docker Error: {e}")
            raise e

    def run_code(self, code: str, dataset: str = None):
        if not self.container:
            raise Exception("Sandbox not active.")

        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode='w') as tar:
            data = code.encode('utf-8')
            info = tarfile.TarInfo(name="script.py")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
            
            if dataset:
                ds_data = dataset.encode('utf-8')
                ds_info = tarfile.TarInfo(name="data.csv")
                ds_info.size = len(ds_data)
                tar.addfile(ds_info, io.BytesIO(ds_data))
                
        tar_stream.seek(0)
        self.container.put_archive("/app", tar_stream)
        
        # 10s timeout remains active for security
        exec_result = self.container.exec_run("timeout 10 python script.py")
        
        if exec_result.exit_code == 124:
            return {"exit_code": 124, "output": "TimeoutError: Scraping or execution took too long (>10s)."}
            
        return {
            "exit_code": exec_result.exit_code,
            "output": exec_result.output.decode("utf-8")
        }

    def stop(self):
        if self.container:
            self.container.remove(force=True)