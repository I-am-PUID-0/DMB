from base import *

def check_processes(process_info):
    found_processes = {key: False for key in process_info.keys()}

    for proc in psutil.process_iter():
        try:
            cmdline = ' '.join(proc.cmdline())
            for process_name, info in process_info.items():
                if info['regex'].search(cmdline):
                    found_processes[process_name] = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return found_processes

try:
    error_messages = []

    if RDAPIKEY and ADAPIKEY and RCLONEMN:
        RCLONEMN_RD = f"{RCLONEMN}_RD"
        RCLONEMN_AD = f"{RCLONEMN}_AD"
    else:
        RCLONEMN_RD = RCLONEMN_AD = RCLONEMN

    mount_type = "serve nfs" if not NFSMOUNT is None and str(NFSMOUNT).lower() == 'true' else "mount"
    
    process_info = {
        "zurg_rd": {
            "regex": re.compile(rf'/zurg/RD/zurg.*--preload', re.IGNORECASE),
            "error_message": "The Zurg RD process is not running.",
            "should_run": str(ZURG).lower() == 'true' and RDAPIKEY 
        },
        "zurg_ad": {
            "regex": re.compile(rf'/zurg/AD/zurg.*--preload', re.IGNORECASE),
            "error_message": "The Zurg AD process is not running.",
            "should_run": str(ZURG).lower() == 'true' and ADAPIKEY 
        },
        "riven_frontend": {
            "regex": re.compile(r'node build'),
            "error_message": "The Riven frontend process is not running.",
            "should_run": str(RIVEN).lower() == 'true' and os.path.exists(f'/data/{RCLONEMN}/__all__')
        },
        "riven_backend": {
            "regex": re.compile(r'/venv/bin/python backend/main.py'),
            "error_message": "The Riven backend process is not running.",
            "should_run": str(RIVEN).lower() == 'true' and os.path.exists(f'/data/{RCLONEMN}/__all__')
        },
        "rclonemn_rd": {
            "regex": re.compile(rf'rclone {mount_type} {re.escape(RCLONEMN_RD)}:'),
            "error_message": f"The Rclone RD process for {RCLONEMN_RD} is not running.",
            "should_run": str(ZURG).lower() == 'true' and RDAPIKEY and os.path.exists(f'/healthcheck/{RCLONEMN}')
        },
        "rclonemn_ad": {
            "regex": re.compile(rf'rclone {mount_type} {re.escape(RCLONEMN_AD)}:'),
            "error_message": f"The Rclone AD process for {RCLONEMN_AD} is not running.",
            "should_run": str(ZURG).lower() == 'true' and ADAPIKEY and os.path.exists(f'/healthcheck/{RCLONEMN}')
        }
    }

    process_status = check_processes(process_info)

    for process_name, info in process_info.items():
        if info["should_run"] and not process_status[process_name]:
            error_messages.append(info["error_message"])

    if error_messages:
        error_message_combined = " | ".join(error_messages)
        raise Exception(error_message_combined)

except Exception as e:
    print(str(e), file=sys.stderr)
    exit(1)
