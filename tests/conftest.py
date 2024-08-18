import pytest

def pytest_addoption(parser):
    parser.addoption("--it8951-driver", action="store")
    parser.addoption("--font-file", action="store")
    parser.addoption("--terminal-nr", action="store")


def pytest_generate_tests(metafunc):
    if 'it8951_driver' in metafunc.fixturenames:
        metafunc.parametrize("it8951_driver", [metafunc.config.option.it8951_driver])

    if 'font_file' in metafunc.fixturenames:
        metafunc.parametrize("font_file", [metafunc.config.option.font_file])

    if 'terminal_nr' in metafunc.fixturenames:
        metafunc.parametrize("terminal_nr", [metafunc.config.option.terminal_nr])
