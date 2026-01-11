## What is the purpose of this program?

This program is designed to run on Windows in the background and collect information about the time spent in various applications. It presents this data in a clear and understandable format.

The program consists of two parts:

- Grabber - collects data while running in the background.

- Analyzer - visualizes and displays the collected data.

## How to automatically run the grabber?

1. Download the executable from the Releases page.

2. Use the following command in Command Prompt with administrator privileges to add the task to Task Scheduler:
   ```shell
    schtasks /create /tn "Program-Using-Logger-grabber" /tr "PATH_TO_grabber.exe" /sc onlogon /delay 0000:01 /f
   ```

3. The grabber will start automatically the next time the computer logs in.

## How to visualize the data?

1. Install Python:
```shell
winget install -e --id Python.Python.3.13
```

2. Install Poetry:
```shell
python -m pip install poetry
```

3. Install this repository (for example, to the Desktop):
```shell
cd .\Desktop
git clone https://github.com/IZomBiee/Program-Using-Logger.git
```
Alternatively, you can download the analyzer separately from GitHub.

4. Go to the analyzer directory and install dependencies using Poetry:
```shell
cd Program-Using-Logger\analyser
poetry install
```

5. Choose how to visualize the data:
```shell
peotry run top_20
poetry run day_timeline
```

## Where data is stored?
The data is stored here in Appdata\Roaming folder:
```shell
cd %appdata%\Program-Using-Logger
```