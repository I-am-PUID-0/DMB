from base import *
from utils.logger import *
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

logger = get_logger()


def chown_single(path, user_id, group_id):
    try:
        os.chown(path, user_id, group_id)
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.error(f"Error changing ownership of '{path}': {e}")


def log_directory_size(directory):
    try:
        num_files = sum([len(files) for r, d, files in os.walk(directory)])
        logger.debug(f"Directory '{directory}' contains {num_files} files.")
    except Exception as e:
        logger.error(f"Error calculating size of directory '{directory}': {e}")


def get_dynamic_workers():
    return multiprocessing.cpu_count()


def chown_recursive(directory, user_id, group_id):
    max_workers = get_dynamic_workers()
    start_time = time.time()
    log_directory_size(directory)
    logger.debug(f"Using {max_workers} workers for chown operation")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for root, dirs, files in os.walk(directory):
            for dir_name in dirs:
                executor.submit(
                    chown_single, os.path.join(root, dir_name), user_id, group_id
                )
            for file_name in files:
                executor.submit(
                    chown_single, os.path.join(root, file_name), user_id, group_id
                )
        executor.submit(chown_single, directory, user_id, group_id)
    end_time = time.time()
    logger.debug(
        f"chown_recursive for {directory} took {end_time - start_time:.2f} seconds"
    )


def create_system_user(username="DMB"):
    try:
        start_time = time.time()
        group_check_start = time.time()
        try:
            grp.getgrgid(group_id)
            logger.debug(f"Group with GID {group_id} already exists.")
        except KeyError:
            logger.debug(f"Group with GID {group_id} does not exist. Creating group...")
            with open("/etc/group", "a") as group_file:
                group_file.write(f"{username}:x:{group_id}:\n")
        group_check_end = time.time()
        logger.debug(
            f"Group check/creation took {group_check_end - group_check_start:.2f} seconds"
        )

        user_check_start = time.time()
        try:
            pwd.getpwnam(username)
            logger.debug(f"User '{username}' with UID {user_id} already exists.")
            return
        except KeyError:
            logger.debug(f"User '{username}' does not exist. Creating user...")
        user_check_end = time.time()
        logger.debug(f"User check took {user_check_end - user_check_start:.2f} seconds")

        home_dir = f"/home/{username}"
        if not os.path.exists(home_dir):
            os.makedirs(home_dir)
        zurg_dir = "/zurg"
        rclone_dir = f"{RCLONEDIR}"
        mnt_dir = "/mnt"
        log_dir = "/log"
        config_dir = "/config"
        riven_dir = "/riven"
        zilean_dir = "/zilean"

        passwd_write_start = time.time()
        with open("/etc/passwd", "a") as passwd_file:
            passwd_file.write(
                f"{username}:x:{user_id}:{group_id}::/home/{username}:/bin/sh\n"
            )
        passwd_write_end = time.time()
        logger.debug(
            f"Writing to /etc/passwd took {passwd_write_end - passwd_write_start:.2f} seconds"
        )
        chown_start = time.time()
        chown_recursive(zurg_dir, user_id, group_id)
        os.chown(rclone_dir, user_id, group_id)
        os.chown(mnt_dir, user_id, group_id)
        chown_recursive(log_dir, user_id, group_id)
        chown_recursive(config_dir, user_id, group_id)
        chown_recursive(riven_dir, user_id, group_id)
        chown_recursive(home_dir, user_id, group_id)
        chown_recursive(zilean_dir, user_id, group_id)
        chown_end = time.time()
        logger.debug(f"Chown operations took {chown_end - chown_start:.2f} seconds")
        end_time = time.time()
        logger.debug(
            f"Total time to create system user '{username}' was {end_time - start_time:.2f} seconds"
        )

    except Exception as e:
        logger.error(f"Error creating system user '{username}': {e}")
        raise
