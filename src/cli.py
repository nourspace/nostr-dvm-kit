import importlib
import inspect
import threading
import time
import structlog
import typer

from client import get_client
from config import env, init_logging
from dvm import BaseDVM

app = typer.Typer()
log = structlog.get_logger()


def load_dvm_from_module(module_name: str, /, **data):
    """
    Dynamically loads the first found dvm class from the given module name
    that inherits from BaseDvm.
    """
    module = importlib.import_module(module_name.rsplit('.', 1)[0])
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, BaseDVM) and name == module_name.rsplit('.', 1)[1] and obj is not BaseDVM:
            return obj(**data)  # Instantiate and return the first found subclass
    raise ValueError(f"No subclass of BaseDvm found in module: {module_name}")


def start_dvm(dvm_instance: BaseDVM):
    dvm_instance.run()


@app.command()
def run(module_names: list[str]):
    init_logging()
    log.info(f"Launching DVMs")
    client = get_client(account=env.str("NOSTR_ADMIN"))
    dvms = [load_dvm_from_module(name, client=client) for name in module_names]
    threads = []

    # Start each dvm in its own thread
    for dvm in dvms:
        thread = threading.Thread(target=start_dvm, args=(dvm,))
        threads.append(thread)
        thread.start()

    try:
        # Keep the main thread running until Ctrl-C is pressed
        while True:
            time.sleep(1)  # Sleep for a short period to reduce CPU usage
    except KeyboardInterrupt:
        log.warn("Received user exit")
        # Call the exit method on all dvms
        for dvm in dvms:
            dvm.exit()
        # Optionally, wait for all threads to complete after calling exit
        for thread in threads:
            thread.join()


if __name__ == "__main__":
    app()
