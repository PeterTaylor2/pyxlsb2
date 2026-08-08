import os
import traceback
import glob

import logging

root_logger = logging.getLogger()

# add to the front of the path so that we can import pyxlsb2 from the source tree instead of an installed version
import sys
home = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(home))

import pyxlsb2

# we also try openpyxl because a good test is to save an .xlsb file
# to .xlsx or .xlsm format and then compare the results

try:
    import openpyxl
except:
    openpyxl = None

def cell_name(row, col):
    """Convert 1-based row and column numbers to an Excel cell reference."""
    letters = ""
    while col:
        col, remainder = divmod(col - 1, 26)
        letters = chr(65 + remainder) + letters
    return "%s%d" % (letters,row)

def log_xls_name(ffn):
    for handler in root_logger.handlers:
        if hasattr(handler, "stream"):
            handler.stream.write("Processing %s\n" % ffn)
            handler.flush()

def parse_xlsb(ffn, ofn, show_values):
    print("parse_xlsb(%s, %s)" % (ffn, ofn))
    with open(ofn, "w") as fp:
        log_xls_name(ffn)
        with pyxlsb2.open_workbook(ffn) as wb:
            for sr in wb.sheets:
                sname = sr.name
                sheet = wb.get_sheet_by_name(sname)
                num_empty_rows = 0
                for row in sheet.rows():
                    has_content = False
                    for cell in row:
                        cname = cell_name(cell.row+1, cell.col+1)
                        try:
                            if cell.value is None and cell.formula is None:
                                continue
                            has_content = True
                            if cell.formula is None or len(cell.formula) == 0:
                                if show_values:
                                    fp.write("%s!%s:{%s}\n" % (sname, cname, cell.value))
                            else:
                                formula = pyxlsb2.formula.Formula.parse(cell.formula, anchor_cell=cell).stringify(wb)
                                if formula.startswith("RC("): continue # indicates shared formula
                                fp.write("%s!%s=%s\n" % (sname, cname, formula))
                        except Exception as e:
                            fp.write("%s!%s: ERROR: %s\n" % (sname, cname, str(e)))

                    if not has_content:
                        num_empty_rows += 1
                        if num_empty_rows >= 100: break
                    else:
                        num_empty_rows = 0

def parse_xls(ffn, ofn, show_values):
    if openpyxl is None:
        raise Exception("openpyxl is not available")

    print("parse_xls(%s, %s)" % (ffn, ofn))

    with open(ofn, "w") as fp:

        # openpyxl workbooks do not support context managers
        wb = None
        try:
            log_xls_name(ffn)
            wb = openpyxl.load_workbook(ffn, read_only=True)
            for sname in wb.sheetnames:
                sheet = wb[sname]
                num_empty_rows = 0
                for row in sheet.rows:
                    has_content = False
                    for cell in row:
                        cname = None
                        try:
                            # in openpyxl cell.value can be a formula object or a value
                            if cell.value is None: continue
                            has_content = True

                            # we cannot just cast to string since not all cell values have a string representation
                            if hasattr(cell.value, "text"):
                                value = cell.value.text
                            else:
                                value = str(cell.value)

                            cname = cell_name(cell.row, cell.column)
                            if value.startswith("="):
                                formula = value[1:]
                                formula = formula.replace("_xll.", "")
                                if formula == "": continue
                                fp.write("%s!%s=%s\n" % (sname, cname, formula))
                            elif show_values:
                                fp.write("%s!%s:{%s}\n" % (sname, cname, value))
                        except Exception as e:
                            fp.write("%s!%s: ERROR: %s\n" % (sname, cname, str(e)))

                    if not has_content:
                        num_empty_rows += 1
                        if num_empty_rows >= 100: break
                    else:
                        num_empty_rows = 0
        finally:
            if wb is not None: wb.close()

def parse_fn(ffn, odn, show_values):
    try:
        fn = os.path.basename(ffn)
        ofn = os.path.join(odn, "%s.txt" % fn)
        if fn.startswith("~"):
            print("ignoring file starting with ~:", fn)
        elif fn.endswith(".xlsb"):
            parse_xlsb(ffn, ofn, show_values)
        elif fn.endswith(".xls") or fn.endswith(".xlsx") or fn.endswith(".xlsm"):
            parse_xls(ffn, ofn, show_values)
        else:
            print("ignoring file with unsupported extension:", fn)
    except Exception as e:
        efn = os.path.join(odn, "error.log")
        with open(efn, "a") as efp:
            efp.write("Error processing %s: %s\n" % (ffn, str(e)))
            efp.write("%s\n" % traceback.format_exc())
        root_logger.error("Error processing %s - see error.log for details" % ffn)

def parse_dn(dn, odn, show_values):
    import glob

    fns = glob.glob(os.path.join(dn, '*.xls*'))
    for ffn in fns:
        parse_fn(os.path.normpath(ffn), odn, show_values)

def main(fns, odn=".", show_values=False, clear_output=False):
    if len(fns) == 0:
        raise Exception("No files or directories provided")

    if os.path.isdir(odn) and clear_output:
        for ffn in glob.glob(os.path.join(odn, "error.log")) + glob.glob(os.path.join(odn, "*.xls*.txt")):
            if os.path.isfile(ffn):
                print("removing %s" % ffn)
                os.remove(ffn)  

    if not os.path.isdir(odn):
        print("creating directory %s" % odn)
        os.makedirs(odn)

    for fn in fns:
        fn = os.path.normpath(fn)
        if os.path.isdir(fn):
            dn = fn
            parse_dn(dn, odn, show_values)
        elif os.path.isfile(fn):
            parse_fn(fn, odn, show_values)

if __name__ == "__main__":
    import getopt
    import sys

    # interactive mode in case we are running the script from a debugger instead of command line
    if len(sys.argv) == 1:
        os.chdir(home)
        print("running %s with no parameters" % sys.argv[0])
        print("current directory:", os.getcwd())
        print()
        while True:
            arg = input("enter argument (including options): ")
            if not arg: break
            sys.argv.append(arg)

    kwargs = {}
    opts, args = getopt.getopt(sys.argv[1:], "o:v", ["warning=", "debug=", "info=", "clear-output"])

    fns = args[:]
    if len(fns) == 0: fns = ["."]
    lfn = None
    clear_output = False
    log_level = None

    for opt in opts:
        if opt[0] == "-o": kwargs["odn"] = opt[1]
        elif opt[0] == "-v": kwargs["show_values"] = True
        elif opt[0] == "--debug":
            lfn = opt[1]
            print("")
            print("Note that DEBUG logging mode is quite heavy and writes a lot of text")
            print("You should probably not do this with more than one file")
            yes = input("Do you want to continue with DEBUG logging (Y/N=<CR>:").upper().startswith("Y")
            if yes:
                print("logging DEBUG to %s" % lfn)
                log_level = logging.DEBUG
        elif opt[0] == "--warning":
            lfn = opt[1]
            print("logging WARNING to %s" % lfn)
            log_level = logging.WARNING
        elif opt[0] == "--info":
            lfn = opt[1]
            print("logging INFO to %s" % lfn)
            log_level = logging.INFO
        elif opt[0] == "--clear-output":
            kwargs["clear_output"] = True
            clear_output = True

    if log_level is not None:
        if clear_output and os.path.isfile(lfn):
            print("removing %s" % lfn)
            os.remove(lfn)
        logging.basicConfig(filename=lfn, level=log_level)

    main(fns, **kwargs)

