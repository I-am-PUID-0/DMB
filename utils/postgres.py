from time import sleep
from base import *
from utils.logger import *
import psycopg2
from psycopg2 import sql
import json


logger = get_logger()


def initialize_postgres_db(db_host, postgres_user, postgres_password, postgres_db):
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=postgres_user,
            password=postgres_password,
            host=db_host,
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [postgres_db]
        )
        if cur.fetchone() is None:
            cur.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(postgres_db), sql.Identifier(postgres_user)
                )
            )
            logger.info(
                f"Database '{postgres_db}' created successfully with owner '{postgres_user}'."
            )
        else:
            logger.info(f"Database '{postgres_db}' already exists.")

        if postgres_db == "postgres":
            logger.info(
                "Checking if pgAgent extension is installed in 'postgres' database..."
            )
            cur.execute("SELECT * FROM pg_extension WHERE extname = 'pgagent';")
            if cur.fetchone() is None:
                cur.execute("CREATE EXTENSION pgagent;")
                logger.info(
                    "pgAgent extension installed successfully in 'postgres' database."
                )
            else:
                logger.info("pgAgent extension already exists in 'postgres' database.")

        if postgres_db == "pgadmin":
            conn_db = psycopg2.connect(
                dbname=postgres_db,
                user=postgres_user,
                password=postgres_password,
                host=db_host,
            )
            conn_db.autocommit = True
            cur_db = conn_db.cursor()
            cur_db.execute("SELECT * FROM pg_extension WHERE extname = 'system_stats';")
            if cur_db.fetchone() is None:
                cur_db.execute("CREATE EXTENSION system_stats;")
                logger.info(
                    f"system_stats extension created in '{postgres_db}' database."
                )
            else:
                logger.info(
                    f"system_stats extension already exists in '{postgres_db}' database."
                )

            cur_db.close()
            conn_db.close()
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
        logger.info(
            f"Created default PostgreSQL configuration file at {config_file_path}."
        )
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
        postmaster_opts = os.path.join(postgres_data, "postmaster.opts")
        if os.path.exists(postmaster_opts):
            logger.debug(
                f"PostgreSQL data directory {postgres_data} already exists and is not empty. Skipping initialization."
            )
            return True
        else:
            logger.info(f"Initializing PostgreSQL data directory at {postgres_data}...")
            initialize_command = f"initdb -D {postgres_data} -U {postgres_user} --pwfile=<(echo {postgres_password})"
            init = process_handler.start_process(
                "PostgreSQL_init",
                postgres_data,
                ["su", postgres_user, "-s", "/bin/sh", "-c", initialize_command],
            )
            init.wait()
            logger.info(f"Initialized PostgreSQL data directory at {postgres_data}.")
            return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error initializing PostgreSQL data directory: {e}")
        return False


def check_postgresql_started(postgres_user, postgres_db, timeout=10):
    logger.info("Checking if PostgreSQL server has started...")
    time.sleep(2)
    start_time = time.time()
    while time.time() - start_time < timeout:
        result = subprocess.run(
            ["pg_isready", "-U", postgres_user, "-d", postgres_db],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            logger.info(f"PostgreSQL server has started.")
            return True
        else:
            logger.info(
                f"PostgreSQL server has not started, waiting... {result.stdout}"
            )
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


def initialize_pgadmin_data_directory(pgadmin_data_dir):
    try:
        if not os.path.exists(pgadmin_data_dir):
            os.makedirs(pgadmin_data_dir, exist_ok=True)
            logger.info(f"Created pgAdmin data directory at {pgadmin_data_dir}.")
        else:
            logger.info(f"pgAdmin data directory exists at {pgadmin_data_dir}.")
        subprocess.run(
            ["chown", "-R", f"{user_id}:{group_id}", pgadmin_data_dir], check=True
        )
        subprocess.run(["chmod", "-R", "700", pgadmin_data_dir], check=True)
        logger.info(f"Changed ownership and set permissions of {pgadmin_data_dir}.")
        return True
    except OSError as e:
        logger.error(f"Error creating pgAdmin data directory: {e}")
        return False


def create_pgadmin_config(pgadmin_data_dir, db_uri):
    config_file_path = os.path.join(pgadmin_data_dir, "config_local.py")

    pgadmin_install_dirs = glob.glob(
        "/pgadmin/venv/lib/python*/site-packages/pgadmin4/"
    )

    if not pgadmin_install_dirs:
        logger.error("pgAdmin installation directory not found.")
        return None

    pgadmin_install_dir = pgadmin_install_dirs[0]
    symlink_path = os.path.join(pgadmin_install_dir, "config_local.py")

    if os.path.exists(config_file_path):
        logger.info(f"pgAdmin configuration file already exists at {config_file_path}.")
    else:
        try:
            with open(config_file_path, "w") as config_file:
                config_file.write("SERVER_MODE = True\n")
                config_file.write(f"DATA_DIR = '{pgadmin_data_dir}'\n")
                config_file.write("DEFAULT_SERVER = '0.0.0.0'\n")
                config_file.write("DEFAULT_SERVER_PORT = 5050\n")
                config_file.write(f"LOG_FILE = '{pgadmin_data_dir}/pgadmin4.log'\n")
                config_file.write(f"CONFIG_DATABASE_URI = '{db_uri}'\n")
                config_file.write(f"SESSION_DB_PATH = '{pgadmin_data_dir}/sessions'\n")
                config_file.write(f"STORAGE_DIR = '{pgadmin_data_dir}/storage'\n")
                config_file.write("DEFAULT_BINARY_PATHS = {\n")
                config_file.write("    'pg': '/usr/bin',\n")
                config_file.write("    'pg-12': '/usr/bin',\n")
                config_file.write("    'pg-13': '/usr/bin',\n")
                config_file.write("    'pg-14': '/usr/bin',\n")
                config_file.write("    'pg-15': '/usr/bin',\n")
                config_file.write("    'pg-16': '/usr/bin',\n")
                config_file.write("    'pg-17': '/usr/bin',\n")
                config_file.write("    'ppas': '/usr/bin',\n")
                config_file.write("    'ppas-12': '/usr/bin',\n")
                config_file.write("    'ppas-13': '/usr/bin',\n")
                config_file.write("    'ppas-14': '/usr/bin',\n")
                config_file.write("    'ppas-15': '/usr/bin',\n")
                config_file.write("    'ppas-16': '/usr/bin',\n")
                config_file.write("    'ppas-17': '/usr/bin'\n")
                config_file.write("}\n")
            logger.info(f"Created pgAdmin configuration file at {config_file_path}.")
        except OSError as e:
            logger.error(f"Error creating pgAdmin configuration file: {e}")
            return None
    try:
        if os.path.exists(symlink_path):
            os.remove(symlink_path)
        os.symlink(config_file_path, symlink_path)
        logger.info(f"Created symlink for config_local.py at {symlink_path}.")
    except OSError as e:
        logger.error(f"Error creating symlink for pgAdmin configuration file: {e}")
        return None

    return config_file_path


def start_pgadmin(process_handler, pgadmin_data_dir, db_uri):
    logger.info("Starting pgAdmin process with external PostgreSQL database...")
    pgadmin_venv = "/pgadmin/venv"

    try:
        config_file_path = create_pgadmin_config(pgadmin_data_dir, db_uri)
        if not config_file_path:
            return False

        env = os.environ.copy()
        env["PATH"] = f"{pgadmin_venv}/bin:" + env["PATH"]
        env["VIRTUAL_ENV"] = pgadmin_venv

        pgadmin_command = f"{pgadmin_venv}/bin/python3 /pgadmin/venv/lib/python*/site-packages/pgadmin4/pgAdmin4.py"
        process_handler.start_process(
            "pgAdmin", pgadmin_data_dir, ["sh", "-c", pgadmin_command], env=env
        )

        logger.info("pgAdmin process started successfully using PostgreSQL database.")
        return True
    except Exception as e:
        logger.error(f"Error starting pgAdmin: {e}")
        return False


def postgres_role_exists(postgres_user, postgres_password, postgres_db, db_host):
    logger.info(f"Checking if role '{postgres_user}' exists...")
    try:
        conn = psycopg2.connect(
            dbname=postgres_db,
            user=postgres_user,
            password=postgres_password,
            host=db_host,
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
            dbname="postgres",
            user=postgres_user,
            password=postgres_password,
            host=db_host,
        )
        cur = conn.cursor()
        cur.execute(
            "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size FROM pg_database;"
        )
        rows = cur.fetchall()
        for row in rows:
            logger.info(f"Database: {row[0]}, Size: {row[1]}")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error listing database sizes: {e}")
        raise


def start_pgagent(process_handler, postgres_user):
    try:
        pgagent_command = (
            f"pgagent host=/var/run/postgresql -f dbname=postgres user={postgres_user}"
        )
        process_handler.start_process(
            "pgAgent", "/var/run/postgresql", ["sh", "-c", pgagent_command]
        )
        return True
    except Exception as e:
        logger.error(f"Error starting pgAgent daemon: {e}")
        return False


def add_pgadmin_server_to_db(pgadmin_db_uri, server_details, timeout=60, interval=5):
    try:
        sleep(5)
        logger.info(
            f"Connecting to pgAdmin database at {pgadmin_db_uri} to add server '{server_details['name']}'..."
        )
        conn = psycopg2.connect(pgadmin_db_uri)
        conn.autocommit = True
        cur = conn.cursor()
        start_time = time.time()
        while time.time() - start_time < timeout:
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'server'
                );
            """
            )
            table_exists = cur.fetchone()[0]

            if table_exists:
                logger.info(
                    "pgAdmin 'server' table exists. Proceeding to check server."
                )
                break
            else:
                logger.info(
                    f"pgAdmin 'server' table does not exist yet. Waiting for {interval} seconds before retrying..."
                )
                time.sleep(interval)
        else:
            logger.error(
                f"Timeout reached after {timeout} seconds. The pgAdmin 'server' table still does not exist."
            )
            cur.close()
            conn.close()
            return False

        try:
            server_port = int(server_details["port"])
        except ValueError:
            logger.error(f"Invalid port value: {server_details['port']}")
            return False
        server_name = server_details["name"].strip()
        server_host = server_details["host"].strip()
        logger.debug(
            f"Checking if server '{server_name}' with host '{server_host}' and port '{server_port}' already exists in the database."
        )
        cur.execute(
            """
            SELECT name, host, port FROM server WHERE name = %s AND host = %s AND port = %s
        """,
            (server_name, server_host, server_port),
        )
        server_exists = cur.fetchone()
        logger.debug(f"Query result: {server_exists}")
        if server_exists:
            logger.info(f"Server '{server_name}' already exists in pgAdmin database.")
            cur.close()
            conn.close()
            return True

        connection_params_json = json.dumps(server_details["connection_parameters"])
        cur.execute(
            """
            INSERT INTO server (user_id, servergroup_id, name, host, port, maintenance_db, username, connection_params)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                1,
                1,
                server_name,
                server_host,
                server_port,
                server_details["maintenance_db"].strip(),
                server_details["username"].strip(),
                connection_params_json,
            ),
        )
        conn.commit()
        logger.info(
            f"Server '{server_name}' added successfully to pgAdmin database. The password will need to be entered in pgAdmin 4 upon first connection."
        )
        cur.close()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"Error adding server to pgAdmin database: {e}")
        return False


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

        subprocess.run(
            ["chown", "-R", f"{user_id}:{group_id}", postgres_data], check=True
        )
        subprocess.run(["chmod", "-R", "700", postgres_data], check=True)
        logger.info(f"Changed ownership and set permissions of {postgres_data}.")

        if not initialize_postgres_data_directory(
            process_handler, postgres_data, postgres_user
        ):
            return False

        if not ensure_run_directory():
            return False

        config_file_path = os.path.join(postgres_data, "postgresql.conf")
        if not os.path.exists(config_file_path):
            logger.warning(
                f"PostgreSQL configuration file not found in {postgres_data}. Creating default configuration."
            )
            if not create_default_postgresql_conf(postgres_data):
                return False
        postgres_command = (
            f"postgres -D {postgres_data} -c config_file={config_file_path}"
        )
        process_handler.start_process("PostgreSQL", postgres_data, postgres_command)

        if not check_postgresql_started(postgres_user, postgres_db="postgres"):
            return False

        if not initialize_postgres_db(
            db_host, postgres_user, postgres_password, "postgres"
        ):
            return False

        if not initialize_postgres_db(
            db_host, postgres_user, postgres_password, postgres_db
        ):
            return False

        if not check_postgresql_ready(
            db_host, postgres_user, postgres_password, postgres_db
        ):
            return False

        if not list_database_sizes(db_host, postgres_user, postgres_password):
            return

        if not PGADMINEMAIL or not PGADMINPASS:
            logger.info(
                "PGADMIN_SETUP_EMAIL or PGADMIN_SETUP_PASSWORD not set. Skipping pgAdmin setup."
            )
            logger.info("PostgreSQL setup completed successfully.")
            return
        else:
            logger.info("Creating pgAdmin database...")
            if not initialize_postgres_db(
                db_host, postgres_user, postgres_password, "pgadmin"
            ):
                return False

            pgadmin_data_dir = "/pgadmin/data"
            if not initialize_pgadmin_data_directory(pgadmin_data_dir):
                return False

            db_uri = (
                f"postgresql://{postgres_user}:{postgres_password}@{db_host}/pgadmin"
            )
            if not start_pgadmin(process_handler, pgadmin_data_dir, db_uri):
                return False

            server_details = {
                "name": "DMB",
                "host": "localhost",
                "port": 5432,
                "maintenance_db": "postgres",
                "username": f"{postgres_user}",
                "connection_parameters": {"connect_timeout": 10},
            }
            pgadmin_db_uri = (
                f"postgresql://{postgres_user}:{postgres_password}@{db_host}/pgadmin"
            )

            if not add_pgadmin_server_to_db(pgadmin_db_uri, server_details):
                logger.error("Failed to add server connection to pgAdmin database.")
                return False

            if not start_pgagent(process_handler, postgres_user):
                return False

            logger.info("PostgreSQL and pgAdmin setup completed successfully.")
