"""Privacy posture audit tool."""
import json
import os
import platform


def audit():
    home = os.path.expanduser('~')
    try:
        home_mode = oct(os.stat(home).st_mode & 0o777)
    except OSError:
        home_mode = 'unknown'

    return {
        'platform': platform.platform(),
        'hostname_exposed': bool(os.getenv('HOSTNAME')),
        'home_permissions': home_mode
    }


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))

