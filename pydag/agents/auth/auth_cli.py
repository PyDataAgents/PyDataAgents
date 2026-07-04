from __future__ import annotations

import argparse
import getpass

from pydag.agents.auth.Auth import AuthManager, Roles

def prompt_password() -> str:
    while True:
        pw1 = getpass.getpass("Password: ")
        pw2 = getpass.getpass("Repeat password: ")

        if pw1 != pw2:
            print("Passwords do not match.")
            continue

        if len(pw1) < 8:
            print("Password must contain at least 8 characters.")
            continue

        return pw1


def main():
    parser = argparse.ArgumentParser("User administration")

    parser.add_argument(
        "--users-file",
        default="users.yaml",
        help="Path to users.yaml",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add-user")
    add.add_argument("username")
    add.add_argument(
        "--roles",
        nargs="*",
        default=[Roles.MEMBER.value],
    )

    delete = sub.add_parser("delete-user")
    delete.add_argument("username")

    passwd = sub.add_parser("change-password")
    passwd.add_argument("username")

    roles = sub.add_parser("set-roles")
    roles.add_argument("username")
    roles.add_argument("roles", nargs="+")

    sub.add_parser("list-users")

    args = parser.parse_args()

    manager = AuthManager(args.users_file)

    try:
        match args.command:
            case "add-user":
                manager.add_user(
                    args.username,
                    prompt_password(),
                    args.roles,
                )
                print("User created.")

            case "delete-user":
                manager.delete_user(args.username)
                print("User deleted.")

            case "change-password":
                manager.change_password(
                    args.username,
                    prompt_password(),
                )
                print("Password changed.")

            case "set-roles":
                manager.set_roles(
                    args.username,
                    args.roles,
                )
                print("Roles updated.")

            case "list-users":
                manager.list_users()

    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
