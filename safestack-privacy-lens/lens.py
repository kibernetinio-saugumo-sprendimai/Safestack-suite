import json, os, platform

def audit():
    return {'platform':platform.platform(),'hostname_exposed':bool(os.getenv('HOSTNAME')),'home_permissions':oct(os.stat(os.path.expanduser('~')).st_mode & 0o777)}
if __name__=='__main__': print(json.dumps(audit(),indent=2))
