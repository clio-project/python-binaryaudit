
import subprocess
from xml.etree import ElementTree

def is_elf(fn):
    with open(fn, "rb") as fd:
        exp = b"\177ELF"
        head = fd.read(4)
    return head == exp

def get_soname_from_xml(xml):
    r = ElementTree.fromstring(xml)
    try:
        return r.attrib["soname"]
    except (AttributeError, KeyError):
        return ""

def serialize(fn):
    cmd = ["abidw", "--no-corpus-path", fn]
    sout = subprocess.PIPE
    serr = subprocess.STDOUT
    shell = False
    try:
        process = subprocess.Popen(cmd, stdout=sout,
                       stderr=serr, shell=shell)
        sout, serr = process.communicate()
        out = "".join([out.decode('utf-8') for out in [sout, serr] if out])
    except OSError as err:
        raise
    # return cmd for logging purposes
    return process.returncode, out, cmd

def compare(ref, cur):
    cmd = ["abidiff", ref, cur]
    sout = subprocess.PIPE
    serr = subprocess.STDOUT
    shell = False
    try:
        process = subprocess.Popen(cmd, stdout=sout,
            stderr=serr, shell=shell)
        sout, serr = process.communicate()
        out = "".join([out.decode('utf-8') for out in [sout, serr] if out])
    except OSError as err:
        raise
    # return cmd for logging purposes
    return process.returncode, out, cmd

DIFF_OK = 0
DIFF_ERROR = 1
DIFF_USAGE_ERROR = 2
DIFF_CHANGE = 4
DIFF_INCOMPATIBLE_CHANGE = 8

def diff_is_ok(c):
    return 0 == c

def diff_is_error(c):
    return (c & 1) == 1

def diff_is_usage_error(c):
    return (c & 2) == 2

def diff_is_change(c):
    return (c & 4) == 4

def diff_is_incompatible_change(c):
    return (c & 8) == 8

def diff_get_bits(c):
    a = []
    if diff_is_ok(c):
        a.append("OK")
    if diff_is_error(c):
        a.append("ERROR")
    if diff_is_usage_error(c):
        a.append("USAGE_ERROR")
    if diff_is_change(c):
        a.append("CHANGE")
    if diff_is_incompatible_change(c):
        a.append("INCOMPATIBLE_CHANGE")

    return a
