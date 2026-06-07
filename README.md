# MAAS

## Run the project with UV
-- UV(based on rust) is used because it is way faster than pip
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
5. Open the Swagger docs to test all the apis
   ```text
   http://127.0.0.1:8000/docs#/v1
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
5. Open the Swagger docs to test all the apis
   ```text
   http://127.0.0.1:8000/docs#/v1
   ```

You can also verify the API endpoint with:
```bash
curl http://127.0.0.1:8000/
```

## Data Model

There are two tables:

1. `deployments` – stores each deployment record, including its `deployment_id`, `model`, `status`, `endpoint_url`, and `api_key`.
   - This is the primary operational record for a deployment lifecycle: create, track, update, and terminate.
2. `deployment_usage` – stores token usage events for each deployment, including `input_tokens`, `output_tokens`, `model`, `api_key`, and `timestamp`.
   - This supports usage analytics, aggregation, and cost estimation over time.

Why this schema:
- It separates deployment metadata from usage, which keeps the system easier to reason about and extend.
- The `deployments` table tracks the resource lifecycle, while `deployment_usage` captures the billing and observability data tied to that lifecycle.
- The schema is intentionally simple and aligned with the current API requirements

Why I use an ORM:
- SQLAlchemy lets me define the schema in Python objects instead of raw SQL, which reduces boilerplate and makes the code more readable.
- It keeps the model and database logic consistent across the app, which makes maintenance and iteration faster.
- Using an ORM also makes the project easier to extend with new fields, relationships, or queries as requirements evolve.

## Scaling
1. Async FastAPI handlers help with I/O-bound work, such as request handling, DB access, and lightweight background tasks. This improves throughput on a single process because the event loop can switch between requests instead of blocking on each one.
2. The real scaling risk in this app is the LLM response path. If the external model call is not implemented with a truly non-blocking client.
   1. We can use some external api for calling model using async handlers, so that the service can serve some other requests while we wait for model api's response
3. We can improve on caching and rate limiting parts, using redis.
4. Regarding database, we can improve on that part using the cluster and not stand alone instance
5. Horizontal scaling
   1. I would use gunicorn server as a process manager (like pm2)
   2. and my workers would be of uvicorn type (so that I could use asyncio features of fastapi)
   3. We can also use auto scaling for the pods acording to the traffi
6. I would also implement monitoring also using any APM, to debug if any issue comes up

## If time permitted, would have used,
1. celery for background tasks
2. redis for count persistance for throttling of completions api 
   1. For now I have used an in memory rate limiter with asnc lock 
3. For migrations and db setup I am using SQLite and `models.Base.metadata.create_all(bind=database.engine)` for initial migrations, We should use more mature tools like `Alembic`

## Trade-offs made
1. Ratelimiting is done using an in memory rate limiter 
   1. Because implementing redis would make it more complex for a POC
   2. Also I did not want to persist this data in sqlite, which will just increase the cost of managing this logs data (This data can be huge) 
2. I have not implemented the cleaning logic for the in memory rate limiter's data because of time constraints
3. Relatively simple ORM models, no back_refs etc for simplicity and development speed
4. 


## Some Divergence from specs ()
1. In specs for the DELETE request on endpoints --> We are supposed to mark it terminated directly 
   1. But it can happen that the process which deletes the deployments failed and actual resource is not terminated but in metadata maintained we are marking it as terminated
   2. I have corrected it with a simulation and asynchronous task in which 
      1. I am initiating a request to delete the resource 
      2. Which is terminated by a backend process in 9/10 times 
      3. for the 1/10 times in which resource is not terminated we can set a process to correct this (eg. cron etc.)
2. Similarly in creating deployment process can fail, so we are marking those entries as failed so we can decide on those later


## I have used AI for,
1. Basic project structure setup like routing, env_vars etc.
2. Brainstorming and reson about certain decisions
   1. choosing an in memory rate limiter over redis usage (for which I would have used a docker compose file to setup everything in one go, It would also go out of the scope of requirement)
3. paraphrasing certain parts of this document itself ;)