# MAAS

## Run the project with UV

1. Install UV if you do not already have it:
   ```bash
   pip install uv
   ```
2. Sync the project dependencies:
   ```bash
   uv sync
   ```
3. Start the app:
   ```bash
   uv run python main.py
   ```
4. Open the app in your browser:
   ```text
   http://127.0.0.1:8000
   ```

## Run the project with pip

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If you are using Git Bash or WSL, use:
   ```bash
   source .venv/bin/activate
   ```
2. Install the project and its dependencies:
   ```bash
   pip install -e .
   ```
3. Start the app:
   ```bash
   python main.py
   ```
4. Open the app in your browser:
   ```text
   http://127.0.0.1:8000
   ```

You can also verify the API endpoint with:
```bash
curl http://127.0.0.1:8000/
```



## Some Divergence from specs ()
1. In specs for the DELETE request on endpoints --> We are supposed to mark it terminated directly 
   1. But it can happen that the process which deletes the deployments failed and actual resource is not terminated but in metadata maintained we are marking it as terminated
   2. I have corrected it with a simulation and asynchronous task in which 
      1. I am initiating a request to delete the resource 
      2. Which is terminated by a backend process in 9/10 times 
      3. for the 1/10 times in which resource is not terminated we can set a process to correct this (eg. cron etc.)
