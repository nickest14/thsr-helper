# thsr-helper
Thsr helper is a command-line tool written in Python that assists users in booking high-speed rail tickets in Taiwan.

## Features
- An easy-to-use CLI interface for booking all kinds of passenger tickets.
- Utilizes TOML configuration to set the environment, including specifying departure date and time ranges.

## Installation
This project is written in python 3.12.
After prepare the python virtual environment and install poetry, pre-commit:
```
poetry install
```

Run the following command to install pre-commit hooks:
```
pre-commit install
```
pre-commit will automatically run the configured hooks.

## Usage

```
$ thsr_helper --help

Usage: thsr_helper [OPTIONS] COMMAND [ARGS]...

A CLI for thsr-helper

Commands:
  booking    Booking or check the ticket.
  config     Check or update config file.

Options:
  --version    -v    Show the application's version and exit.
  --help             Show this message and exit.
```

### Config

```
$ thsr_helper config --help

Usage: thsr_helper config [OPTIONS] COMMAND [ARGS]...

Check or update config file

Commands:
  ls        Show the config settings
  update    Update the config file

Options:
  --help    Show this message and exit.
```

### Booking

```
$ thsr_helper booking --help

Usage: thsr_helper booking [OPTIONS] COMMAND [ARGS]...

Booking or check the ticket

Commands:
  ls        Check the booking history
  order    Booking the ticket

Options:
  --help    Show this message and exit.
```

Ticket info will be saved in the path thsr_helper/.db/history.json