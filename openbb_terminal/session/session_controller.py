from typing import Tuple

from prompt_toolkit import PromptSession

import openbb_terminal.session.local_model as Local
from openbb_terminal import terminal_controller
from openbb_terminal.core.config.paths import PACKAGE_DIRECTORY
from openbb_terminal.rich_config import console
from openbb_terminal.session.session_model import (
    LoginStatus,
    create_session,
    login,
)


def display_welcome_message():
    """Display welcome message"""
    with open(PACKAGE_DIRECTORY / "session" / "banner.txt") as f:
        console.print(f"[menu]{f.read()}[/menu]\n")
        console.print("Register     : [cmds]https://my.openbb.co/register[/cmds]")
        console.print("Ask support  : [cmds]https://openbb.co/support[/cmds]")


def get_user_input() -> Tuple[str, str, bool]:
    """Get user input

    Returns
    -------
    Tuple[str, str, bool]
        The user email, password and save login option.
    """
    console.print(
        "[info]\nPlease enter your credentials or press enter for guest mode:[/info]"
    )

    s: PromptSession = PromptSession()

    email = s.prompt(
        message="> Email: ",
    )
    if not email:
        return "", "", False

    password = s.prompt(
        message="> Password: ",
        is_password=True,
    )
    save_str = s.prompt(message="> Remember me? (y/n): ", is_password=False).lower()
    save = False
    if save_str == "y":
        save = True

    return email, password, save


def prompt(welcome=True, guest_allowed=False):
    """Prompt and launch terminal if login is successful.

    Parameters
    ----------
    welcome : bool, optional
        Display welcome message, by default True
    """
    if welcome:
        display_welcome_message()

    while True:
        email, password, save = get_user_input()
        if not email or not password:
            if guest_allowed:
                return launch_terminal()
            continue

        session = create_session(email, password, save)
        if isinstance(session, dict) and session:
            return login_and_launch(session=session, guest_allowed=guest_allowed)


def launch_terminal():
    """Launch terminal"""
    terminal_controller.parse_args_and_run()


def login_and_launch(session: dict, guest_allowed: bool = True):
    """Login and launch terminal.

    Parameters
    ----------
    session : dict
        The session info.
    guest_allowed : bool, optional
        Allow guest login, by default True
    """
    status = login(session)
    if status == LoginStatus.SUCCESS:
        launch_terminal()
    elif status == LoginStatus.FAILED:
        prompt(welcome=False, guest_allowed=guest_allowed)
    else:
        prompt(welcome=True, guest_allowed=guest_allowed)


def main(guest_allowed: bool = True):
    """Main function

    Parameters
    ----------
    guest_allowed : bool, optional
        Allow guest login, by default True
    """
    local_session = Local.get_session()
    if not local_session:
        prompt(guest_allowed=guest_allowed)
    else:
        login_and_launch(session=local_session, guest_allowed=guest_allowed)


if __name__ == "__main__":
    main()
