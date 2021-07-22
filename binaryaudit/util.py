import os


def _note(*args):
    print(''.join(args))


def _warn(*args):
    print("WARNING: " + ''.join(args))


def _error(*args):
    print("ERROR: " + ''.join(args))


def create_path_to_xml(sn, adir, fn):
    ''' Returns the path through adir to an xml file given its filename or soname
    Parameters:
        sn (str): soname generated from xml file
        adir (str): path to abixml directory
        fn (str): filename
    '''
    if len(sn) > 0:
        # XXX This won't handle multiple soname within the same
        #     recipe. However it's half as bad as with multiple
        #     library versions recipe names need to be different.
        sn_split = sn.split(".")

        if 1 == len(sn_split):
            out_fn = os.path.join(adir, sn)
        else:
            nl = []
            for p in sn_split:
                nl.append(p)
                if "so" == p:
                    break
            nl.append("xml")
            out_fn = os.path.join(adir, ".".join(nl))

    else:
        out_fn = os.path.join(adir, ".".join([os.path.basename(fn), "xml"]))

    return out_fn
