from base import *
from utils.logger import *


logger = get_logger()


def chown_recursive(directory, user_id, group_id):
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            try:
                os.chown(os.path.join(root, dir_name), user_id, group_id)
            except FileNotFoundError as e:
                continue
            except Exception as e:
                logger.error(f"Error changing ownership of directory '{dir_name}': {e}")

        for file_name in files:
            try:
                os.chown(os.path.join(root, file_name), user_id, group_id)
            except FileNotFoundError as e:
                continue
            except Exception as e:
                logger.error(f"Error changing ownership of file '{file_name}': {e}")
    try:
        os.chown(directory, user_id, group_id)
    except FileNotFoundError as e:
        pass
    except Exception as e:
        logger.error(f"Error changing ownership of directory '{directory}': {e}")


def create_system_user(username="DMB"):
    try:
        try:
            grp.getgrgid(group_id)
            logger.debug(f"Group with GID {group_id} already exists.")
        except KeyError:
            logger.debug(f"Group with GID {group_id} does not exist. Creating group...")
            with open("/etc/group", "a") as group_file:
                group_file.write(f"{username}:x:{group_id}:\n")

        try:
            pwd.getpwnam(username)
            logger.debug(f"User '{username}' with UID {user_id} already exists.")
            return
        except KeyError:
            logger.debug(f"User '{username}' does not exist. Creating user...")

        home_dir = f"/home/{username}"
        if not os.path.exists(home_dir):
            os.makedirs(home_dir)
        zurg_dir = "/zurg"
        rclone_dir = f"{RCLONEDIR}"
        mnt_dir = "/mnt"
        log_dir = "/log"
        config_dir = "/config"
        riven_dir = "/riven"

        with open("/etc/passwd", "a") as passwd_file:
            passwd_file.write(
                f"{username}:x:{user_id}:{group_id}::/home/{username}:/bin/sh\n"
            )
        chown_recursive(zurg_dir, user_id, group_id)
        os.chown(rclone_dir, user_id, group_id)
        os.chown(mnt_dir, user_id, group_id)
        chown_recursive(log_dir, user_id, group_id)
        chown_recursive(config_dir, user_id, group_id)
        chown_recursive(riven_dir, user_id, group_id)
        chown_recursive(home_dir, user_id, group_id)
        logger.debug(
            f"Created system user '{username}' with UID {user_id} and GID {group_id}."
        )

    except Exception as e:
        logger.error(f"Error creating system user '{username}': {e}")
        raise
