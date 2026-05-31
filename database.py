import os
import ibm_db

DB2_DSN = (
    f"DATABASE={os.getenv('DB2_DATABASE', 'SIGRI')};"
    f"HOSTNAME={os.getenv('DB2_HOST', '172.25.2.10')};"
    f"PORT={os.getenv('DB2_PORT', '50000')};"
    f"PROTOCOL=TCPIP;"
    f"UID={os.getenv('DB2_USER', 'salfamwb')};"
    f"PWD={os.getenv('DB2_PASSWORD', 'C0nsul_W3b#')};"
)


def get_connection():
    return ibm_db.connect(DB2_DSN, "", "")
