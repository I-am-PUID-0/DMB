from base import *
from utils.logger import *
import psycopg2
from psycopg2 import sql


logger = get_logger()


def initialize_postgres_db(db_host, postgres_user, postgres_password, postgres_db):
    try:
        conn = psycopg2.connect(
            dbname='postgres',  
            user=postgres_user,
            password=postgres_password,
            host=db_host
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [postgres_db])
        if cur.fetchone() is None: 
            cur.execute(sql.SQL("CREATE DATABASE {} OWNER {}").format(
                sql.Identifier(postgres_db),
                sql.Identifier(postgres_user)
            ))
            logger.info(f"Database '{postgres_db}' created successfully with owner '{postgres_user}'.")
            cur.close()
            conn.close()
            return True
        else:
            logger.info(f"Database '{postgres_db}' already exists.")
            cur.close()
            conn.close()
            return True
    except Exception as e:
        logger.error(f"Error initializing PostgreSQL database: {e}")
        return False 

def create_default_postgresql_conf(postgres_data):
    config_file_path = os.path.join(postgres_data, "postgresql.conf")
    try:
        with open(config_file_path, "w") as config_file:
            config_file.write("# PostgreSQL configuration file\n")
            config_file.write("listen_addresses = '*'\n")
            config_file.write("port = 5432\n")
            config_file.write("max_connections = 100\n")
            config_file.write("shared_buffers = 128MB\n")
        logger.info(f"Created default PostgreSQL configuration file at {config_file_path}.")
        return True
    except OSError as e:
        logger.error(f"Error creating PostgreSQL configuration file: {e}")
        return False

def ensure_run_directory():
    try:
        run_dir = "/run/postgresql"
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)
            logger.debug(f"Created directory {run_dir}.")
        subprocess.run(["chown", "-R", f"{user_id}:{group_id}", run_dir], check=True)
        subprocess.run(["chmod", "775", run_dir], check=True)
        logger.debug(f"Set ownership and permissions for {run_dir}.")
        return True
    except Exception as e:
        logger.error(f"Error setting up /run/postgresql directory: {e}")
        return False

def initialize_postgres_data_directory(process_handler, postgres_data, postgres_user):
    try:
        postmaster_opts = os.path.join(postgres_data, 'postmaster.opts')
        if os.path.exists(postmaster_opts):
            logger.debug(f"PostgreSQL data directory {postgres_data} already exists and is not empty. Skipping initialization.")
            return True
        else:
            logger.info(f"Initializing PostgreSQL data directory at {postgres_data}...")
            initialize_command = f"initdb -D {postgres_data} -U {postgres_user} --pwfile=<(echo {postgres_password})"
            init = process_handler.start_process("PostgreSQL_init", postgres_data, ["su", postgres_user, "-s", "/bin/sh", "-c", initialize_command])
            init.wait()
            logger.info(f"Initialized PostgreSQL data directory at {postgres_data}.")
            return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error initializing PostgreSQL data directory: {e}")
        return False

def check_postgresql_started(timeout=10):
    logger.info("Checking if PostgreSQL server has started...")
    time.sleep(2)
    start_time = time.time()   
    while time.time() - start_time < timeout:
        result = subprocess.run(["pg_isready"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("PostgreSQL server has started.")
            return True
        else:
            logger.info("PostgreSQL server has not started, waiting...")
        time.sleep(1)
    logger.error("PostgreSQL server failed to start within the timeout period.")
    return False

def check_postgresql_ready(db_host, postgres_user, postgres_password, postgres_db):
    logger.info("Checking if PostgreSQL database is accessible...")
    for _ in range(30):  
        try:
            conn = psycopg2.connect(
                dbname=postgres_db,
                user=postgres_user,
                password=postgres_password,
                host=db_host,
            )
            conn.close()
            logger.info("PostgreSQL database is accessible.")
            return True
        except psycopg2.OperationalError as e:
            logger.info(f"Waiting for PostgreSQL database to be accessible... {e}")
            time.sleep(2)
    logger.error("PostgreSQL database was not accessible within the timeout period.")
    return False

def postgres_role_exists(postgres_user, postgres_password, postgres_db, db_host):
    logger.info(f"Checking if role '{postgres_user}' exists...")
    try:
        conn = psycopg2.connect(
            dbname=postgres_db,
            user=postgres_user,
            password=postgres_password,
            host=db_host
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname=%s;", (postgres_user,))
        role_exists = cur.fetchone() is not None
        cur.close()  
        conn.close()  
        return role_exists
    except Exception as e:
        logger.error(f"Error checking if role '{postgres_user}' exists: {e}")
        raise

def list_database_sizes(db_host, postgres_user, postgres_password):
    logger.info("Listing PostgreSQL database sizes...")
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=postgres_user,
            password=postgres_password,
            host=db_host
        )
        cur = conn.cursor()
        cur.execute("SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size FROM pg_database;")
        rows = cur.fetchall()
        for row in rows:
            logger.info(f"Database: {row[0]}, Size: {row[1]}")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error listing database sizes: {e}")
        raise

def postgres_setup(process_handler=None):
    logger.info("Setting up PostgreSQL...")
    if postgres_data:
        if not os.path.exists(postgres_data):
            try:
                os.makedirs(postgres_data, exist_ok=True)
                logger.info(f"Created PostgreSQL data directory at {postgres_data}.")
            except OSError as e:
                logger.error(f"Error creating PostgreSQL data directory: {e}")
                return
        else:
            logger.info(f"PostgreSQL data directory exists at {postgres_data}.")

        subprocess.run(["chown", "-R", f"{user_id}:{group_id}", postgres_data], check=True)
        subprocess.run(["chmod", "-R", "700", postgres_data], check=True)
        logger.info(f"Changed ownership and set permissions of {postgres_data}.")

        if not initialize_postgres_data_directory(process_handler, postgres_data, postgres_user):
            return False

        if not ensure_run_directory():
            return False

        config_file_path = os.path.join(postgres_data, "postgresql.conf")
        if not os.path.exists(config_file_path):
            logger.warning(f"PostgreSQL configuration file not found in {postgres_data}. Creating default configuration.")
            if not create_default_postgresql_conf(postgres_data):
                return False
        postgres_command = f"postgres -D {postgres_data} -c config_file={config_file_path}"        
        #process_handler.start_process("PostgreSQL", postgres_data, ["su", "DMB", "-s", "/bin/sh", "-c", postgres_command])
        process_handler.start_process("PostgreSQL", postgres_data, postgres_command)

        if not check_postgresql_started():
            return False

        if not initialize_postgres_db(db_host, postgres_user, postgres_password, postgres_db):
            return False

        if not check_postgresql_ready(db_host, postgres_user, postgres_password, postgres_db):
            return False

        if not list_database_sizes(db_host, postgres_user, postgres_password):
            return