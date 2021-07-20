try:
    import bb as util
    util.note = bb.note  # noqa: F821
    util.warn = bb.warn  # noqa: F821
    util.error = bb.error  # noqa: F821
except BaseException:
    from binaryaudit import util
    util.note = util._note
    util.warn = util._warn
    util.error = util._error
