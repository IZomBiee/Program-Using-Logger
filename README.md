## What is the purpose of this program?

This program is designed to run in the background and collect information about the time spent in various applications. It presents this data in a clear and understandable format.

---

## How to use it?

The program is intended to run automatically at system startup. However, to run it manually:

1. Navigate to the project directory:
   ```shell
   cd Desktop\\program-using-logger
   ```

2. Install dependencies using Poetry and run `main.py`:
   ```shell
   poetry install
   poetry run python main.py
   ```

---

## How to add it to startup on Windows?

1. Go to the project directory, install dependencies, and run the following command to get the path to the virtual environment's Python interpreter:
   ```shell
   poetry env info --executable
   ```

2. Copy the returned path, replace `python.exe` with `pythonw.exe`.

3. Then use this command in Command Prompt with admin privileges to add the task to Task Scheduler:
   ```shell
    schtasks /create /tn "Program Logger" /tr "PATH_TO_PYTHONW PATH_TO_MAIN.PY" /sc onlogon /delay 0001:00 /f
   ```

   Replace `PATH_TO_PYTHONW` with the path you got in step 2, and `PATH_TO_MAIN.PY` with the full path to project main.py.

---

## How to view statistics?

To view statistics, run the appropriate script from the `visualization` folder. For example, to see the top 20 most-used programs within a specific time range:

```shell
poetry run python visualization\\top_20.py
```