from binaryaudit import util
from binaryaudit import abicheck
import os
import glob


def build_name(sn, adir, fn):
    if len(sn) > 0:
        # XXX This won't handle multiple soname within the same
        #     recipe. However it's half as bad as with multiple
        #     library versions recipe names need to be different.
        l = sn.split(".")

        if 1 == len(l):
            out_fn = os.path.join(adir, sn)
        else:
            nl = []
            for p in l:
                nl.append(p)
                if "so" == p:
                    break
            nl.append("xml")
            out_fn = os.path.join(adir, ".".join(nl))
               
    else:
        out_fn =  os.path.join(adir, ".".join([os.path.basename(fn), "xml"]))

    return out_fn


def build_all_xml(adir, id):
    for fn in glob.iglob(id + "/**/**", recursive = True):
        if os.path.isfile(fn) and not os.path.islink(fn):
                if not abicheck.is_elf(fn):
                    continue
                # If there's no error, out is the XML representation
                ret, out, cmd = abicheck.serialize(fn)
                util.note(" ".join(cmd))
                if not 0 == ret:
                    util.error(out)
                    return                
                if not out:
                    util.warn("Empty dump output for '{}'".format(fn))
                    return

                sn = abicheck.get_soname_from_xml(out)
                
                bn = build_name(sn, adir, fn)

                




