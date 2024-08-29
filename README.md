# e-ink-console

## Installation
Use a somewhat recent version of Python. It's also recommended to use a virtual environment. Create one with `python -m venv .venv` and then activate it with `source .venv/bin/activate`. Now you can install the dependencies with `pip install -r requirements.txt`.

## Tests
Be sure to run the tests with `python -m pytest`. That way the imports should work automatically.


## Run the console
The console will use one of your `/dev/tty` devices. Usually you will already have `/dev/tty1` running your current session so `/dev/tty2` should probably work.

An example of how you may invoke this tool:
`python -m e_ink_console --font-file /usr/share/fonts/TTF/DejaVuSansMono.ttf  --it8951-driver ../rust-it8951/target/debug/examples/cli --terminal-nr 2`

The tool will automatically decide settings for the screen.
