from celery import Celery

# For Redis, the broker URL is redis://<host>:<port>/<db_number>
# Our redis service is named 'redis' in docker-compose.
broker_url = "redis://redis:6379/0"
result_backend = "redis://redis:6379/0"

# Create the Celery app instance
# The first argument is the name of the current module.
# The 'include' argument is a list of modules to import when the worker starts.
celery_app = Celery(
    "worker",
    broker=broker_url,
    backend=result_backend,
    include=["app.tasks.email_tasks"]
)