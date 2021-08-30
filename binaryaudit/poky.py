
import os
import time
import tempfile
import shutil
import tarfile
import glob
import argparse
from binaryaudit import util
from binaryaudit import abicheck
from binaryaudit import cli
from binaryaudit.db import VERSION_NOT_AVAILABLE
from binaryaudit.db import TRANSACTION_MAIN_RESULT_FAILED, TRANSACTION_MAIN_RESULT_PASSED, TRANSACTION_MAIN_RESULT_PENDING
import sys
from binaryaudit.cli import arg_parser, arg_parser_rpm

args = cli.arg_parser.parse_args()


def retrieve_baseline(db_conn, prod_id):
    ''' Fetch buildhistory baseline data from the db and extract for the further usage.

        Parameters:

        Returns:
            baseline_id (int): Baseline ID from DB.
            baseline_dir (str): Path to the extracted buildhistory baseline directory.
    '''
    baseline_id, baseline_data = db_conn.get_ba_latest_baseline(prod_id)
    if not baseline_id:
        util.error("Couldn't find a matching product ID.")
        return None, None
    util.debug("baseline_id: '{}'\n".format(baseline_id))

    data_fl = tempfile.NamedTemporaryFile(delete=False)
    data_fl.write(baseline_data)
    data_fl.flush()
    data_fl.close()

    # TODO Perhaps use a better random path.
    extractdir = "/tmp/binaryaudit_base"
    if os.path.isdir(extractdir):
        shutil.rmtree(extractdir)
    os.makedirs(extractdir)

    with tarfile.open(data_fl.name, "r:gz") as tgz:
        tgz.extractall(extractdir)
        tgz.close()
    os.unlink(data_fl.name)
    # Depends on how we pack, but the first sibling named "buildhistory" should be it.
    buildhistory_baseline_dir = None
    for root, dirs, files in os.walk(extractdir):
        if "buildhistory" in dirs:
            buildhistory_baseline_dir = os.path.join(root, "buildhistory")
            break
    if not buildhistory_baseline_dir and not os.path.isdir(buildhistory_baseline_dir):
        util.error("Couldn't setup buildhistory baseline.")

    return baseline_id, buildhistory_baseline_dir


def _get_dump_duration(recipe_binaudit_path):
    ret = .0
    fl = recipe_binaudit_path + "/abixml.duration"
    try:
        with open(fl, "r") as f:
            ret = float(f.read())
            f.close()
    except Exception:
        pass
    return ret


def _get_version_from_buildhistory(d):
    latest_fl = os.path.join(d, "latest")
    version = VERSION_NOT_AVAILABLE
    try:
        with open(latest_fl, "r") as f:
            for ln in f.readlines():
                a = ln.split("=")
                if "PV" == a[0].rstrip().lstrip():
                    version = a[1].rstrip().lstrip()
    except Exception:
        pass
    return version


def recipe_abicheck(recipe_binaudit_path, buildhistory_baseline_dir, bulidhistory_current_dir, suppressions):
    t0 = time.monotonic()
    ret_acc = abicheck.DIFF_OK
    dump_duration = _get_dump_duration(recipe_binaudit_path)

    for cur_xml_fl in glob.glob(recipe_binaudit_path + "/abixml/*.xml", recursive=False):
        with open(cur_xml_fl) as f:
            xml = f.read()
            f.close()

        # Care only about DSO for now
        sn = abicheck.get_soname_from_xml(xml)
        # XXX Handle error cases, eg xml file was garbage, etc.
        if len(sn) > 0:
            ref_xml_fl = cur_xml_fl.replace(bulidhistory_current_dir, buildhistory_baseline_dir)
            if not os.path.isfile(ref_xml_fl):
                continue
            ret, out, cmd = abicheck.compare(ref_xml_fl, cur_xml_fl, suppressions)
            if ret > ret_acc:
                # just get the highest score
                ret_acc = ret

    t1 = time.monotonic()

    new_base = os.path.dirname(recipe_binaudit_path)
    old_base = new_base.replace(bulidhistory_current_dir, buildhistory_baseline_dir)

    item_name = os.path.basename(new_base)

    new_version = _get_version_from_buildhistory(new_base)
    base_version = _get_version_from_buildhistory(old_base)

    # Take into account the time spent for serialization during the build, too.
    exec_time = int(dump_duration + (t1-t0)*1000000)  # usec

    result = abicheck.diff_get_bit(ret_acc)
    if 0 == ret_acc:
        res_details = ""
    else:
        res_details = out

    return item_name, base_version, new_version, exec_time, result, res_details, ret_acc

def poky_binary_audit(all_suppressions):
    

    db_conn = None
    if 'y' == args.enable_telemetry:
        try:
            cli.validate_telemetry_args(args)
        except argparse.ArgumentError as e:
            util.fatal(str(e))
            sys.exit(3)

        from binaryaudit.db import wrapper as db_wrapper
        try:
            db_conn = db_wrapper(args.db_config, util.logger)
            db_conn.initialize_db()
        except Exception as e:
            util.error(str(e))

    if args.compare_buildhistory:
        d1 = args.buildhistory_baseline
        d2 = args.buildhistory_current

        out_dir = args.output_dir
        # XXX err out if exists or remove existing?
        if out_dir and not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        if not 'y' == args.enable_telemetry and not os.path.isdir(d1):
                util.warn("Directory '{}' doesn't exist.".format(d1))
                sys.exit(1)
        # Either need the baseline directory passed or telemetry enabled
        # to fetch the baseline.
        if not os.path.isdir(d2):
                util.warn("Directory '{}' doesn't exist.".format(d2))
                sys.exit(1)

        if 'y' == args.enable_telemetry:
            prod_id = db_conn.get_product_id(args.product_name, args.derivative)
            if not prod_id:
                util.error("Couldn't find a matching product ID.")
                sys.exti(1)
            util.debug("product_id: '{}'".format(prod_id))

            if d1:
                util.warn("Telemetry is enabled, ignoring the supplied buildhistory baseline.")
            baseline_id, d1 = retrieve_baseline(db_conn, prod_id)
            if not baseline_id or not d1:
                sys.exit(1)

            db_conn.insert_main_transaction(args.build_id, prod_id, args.buildurl,
                                            args.logurl, TRANSACTION_MAIN_RESULT_PENDING, baseline_id)

        build_ret_acc = abicheck.DIFF_OK
        build_result = TRANSACTION_MAIN_RESULT_PASSED

        import glob
        # Only iterate through packages for now.
        # Only iterate through d2 now. Reverse iteration might bake sense, too.
        for fn in glob.glob(d2 + "/packages/*/*/binaryaudit", recursive=False):
            item_name, base_version, new_version, exec_time, result, res_details, ret_acc = recipe_abicheck(fn, d1, d2, all_suppressions)

            # Set the build accumulated value to the highest found score.
            if ret_acc > build_ret_acc:
                build_ret_acc = ret_acc

            util.debug("item: '{}', base: '{}', new: '{}', duration: '{}', res: '{}'".format(item_name, base_version, new_version, exec_time, result))

            if 'y' == args.enable_telemetry:
                db_conn.insert_ba_transaction_details(args.build_id, prod_id, item_name, base_version, new_version, exec_time, result, res_details)

            if out_dir and abicheck.DIFF_OK != ret_acc:
                fname = util.build_diff_filename(item_name, base_version, new_version)
                out_fpath = os.path.join(out_dir, fname)
                with open(out_fpath, "w") as f:
                    f.write(res_details)

        if 'y' == args.enable_telemetry:
            if abicheck.DIFF_OK != build_ret_acc:
                build_result = TRANSACTION_MAIN_RESULT_FAILED
            db_conn.update_ba_test_result(args.build_id, prod_id, build_result)
        sys.exit(build_ret_acc)
    elif args.insert_baseline:
        if 'n' == args.enable_telemetry:
            # Another way would be to implicitly enable telemetry
            util.error("Telemetry is not anabled")
            sys.exit(1)

        product_id = db_conn.get_product_id(args.product_name, args.derivative)

        db_conn.insert_main_transaction(args.build_id, product_id, args.buildurl, args.logurl, TRANSACTION_MAIN_RESULT_PASSED)

        data = None
        with open(args.insert_baseline, "rb") as f:
            data = f.read()
            f.close
        db_conn.insert_ba_baseline_data(args.build_id, product_id, data)
