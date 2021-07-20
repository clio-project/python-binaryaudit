import glob
import os
from binaryaudit import abicheck
try:
    import bb as util
    util.note = bb.note
    util.warn = bb.warn
    util.error = bb.error
except:
    from binaryaudit import util
    util.note = util._note
    util.warn = util._warn
    util.error = util._error



