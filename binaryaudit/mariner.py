from binaryaudit import conf
from binaryaudit import abicheck
from binaryaudit import dnf

def binary_audit(source_dir, output_dir, build_id, product_id, db_conn):
    new_json_file = conf.get_config("Mariner", "new_json_file_name")
    old_json_file = conf.get_config("Mariner", "old_json_file_name")
    abicheck.generate_package_json(source_dir, new_json_file)
    dnf.process_downloads(source_dir, new_json_file, old_json_file, output_dir, build_id, product_id, db_conn)
