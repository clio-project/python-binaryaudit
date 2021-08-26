import os
import shutil

from binaryaudit import conf
from binaryaudit import abicheck
from binaryaudit import dnf


def binary_audit(source_dir, output_dir, build_id, product_id, db_conn, use_suppressions, cleanup):
    new_json_file = conf.get_config("Mariner", "new_json_file_name")
    old_json_file = conf.get_config("Mariner", "old_json_file_name")
    try:
        remaining_files = abicheck.generate_package_json(source_dir, new_json_file)
        result = dnf.process_downloads(source_dir, new_json_file, old_json_file, output_dir,
                                       build_id, product_id, db_conn, remaining_files, use_suppressions)
    finally:
        cleanup_temp(cleanup, source_dir, new_json_file, old_json_file)
    return result

                        
def cleanup_temp(cleanup, source_dir, new_json_file, old_json_file):
    if cleanup is True:
        try:
            shutil.rmtree(source_dir + "old")
            os.remove(new_json_file)
            os.remove(old_json_file)
            os.remove("output_file")
        except OSError:
            pass
