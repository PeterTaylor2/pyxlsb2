##########################################################################
# This script installs the development version of pyxlsb2 package (from
# the pyxlsb2 directory) to the so-called usersitepackages directory.
#
# usersitepackages is defined by site.getusersitepackages() function
# and refers to a directory that is placed by python in the path before
# the regular site-packages directory.
#
# Hence you can avoid all the issues of trying to prepare and install
# packages via pip.
#
# The idea is that you copy the code into usersitepackages by running
#            <python> install-user.py
# where <python> represents your version of python however that is
# determined in your particular development environment.
#
# Then you can edit and debug the code in usersitepackages using your
# favourite python development platform until you have fixed any problems.
#
# After this process is complete then you can restore that version of
# pyxlsb2 to your local directory by using the -r options:
#            <python> install-user.py -r
# and subsequently commit to source control.
##########################################################################
import os
import site
import glob
import sys
import filecmp
import shutil

def get_target():
    dn = site.getusersitepackages()
    odn = os.path.join(dn, "pyxlsb2")

    if not(os.path.isdir(odn)):
        print("creating %s" % odn)
        os.makedirs(odn)

    return odn

def copy_file(src, dst, verbose=False):
    if not os.path.isfile(src):
        raise Exception("Source file %s is not a file" % os.path.normpath(src))

    if not os.path.isfile(dst):
        copy_source = True
        ddn = os.path.dirname(dst)
        if ddn and not os.path.isdir(ddn):
            print("creating directory %s" % ddn)
            os.makedirs(ddn)
    else: copy_source = not filecmp.cmp(src, dst)

    if copy_source:
        print("copying %s" % dst)
        shutil.copy2(src, dst)
    elif verbose:
        print("not copying %s - unchanged" % dst)

    return copy_source

def main(src, dst, clean=False, verbose=False, yes=False):

    print("copying from %s to %s (clean=%s)" % (src,dst,clean))
    if not yes:
        yes = input("Continue with the copy (Y/N=<CR>): ").upper().startswith("Y")
        if not yes:
            print_help()
            return
    count = 0

    pattern = os.path.join(src, "*.py")
    if verbose:
        print("source files pattern: %s" % pattern)

    ffns = glob.glob(pattern)
    if verbose:
        import pprint
        print("files to be copied:")
        pprint.pprint(ffns)

    for ffn in ffns:
        fn = os.path.basename(ffn)
        ifn = ffn
        ofn = os.path.join(dst, fn)
        count += copy_file(ifn, ofn, verbose=verbose)

    if clean:
        bfns = set([os.path.basename(ffn) for ffn in ffns])
        for fn in os.listdir(dst):
            ffn = os.path.join(dst, fn)
            if fn not in bfns:
                if os.path.isdir(ffn):
                    print("removing directory %s" % ffn)
                    shutil.rmtree(ffn, ignore_errors=True)
                else:
                    print("removing %s" % ffn)
                    os.remove(ffn)

    if count > 0:
        print("%d file%s copied to %s" % (count, "s" if count > 1 else "", dst))

def print_help():
    print()
    print("%s: installs the software from pyxlsb2 directory to user site-packages directory" % sys.argv[0])
    print()
    print("Before the copy you will be prompted whether you wish to continue unless you use the -y option")
    print()
    print("No command line arguments accepted - only options beginning with - or --")
    print()
    print("Options are as follows:")
    print("   -c or --clean:   Clean the target directory")
    print("   -v or --verbose: Print extra information")
    print("   -r or --reverse: Copy from user site-packages to the pyxlsb2 directory")
    print("   -y:              Don't prompt for whether you wish to continue")
    print("   -h or --help:    Print this message and exit")

if __name__ == "__main__":
    import getopt

    home = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(home, "pyxlsb2")
    dst = get_target()

    try:
        opts,args = getopt.getopt(sys.argv[1:], "vrchy",
                                  ["clean", "help", "reverse", "verbose"])

        if len(args) != 0:
            raise Exception("No parameters - only options")

        kwargs = {}
        reverse = False
        for opt in opts:
            if opt[0] == "-c" or opt[0] == "--clean":
                kwargs["clean"] = True
            elif opt[0] == "-v" or opt[0] == "--verbose":
                kwargs["verbose"] = True
            elif opt[0] == "-h" or opt[0] == "--help":
                print_help()
                exit(0)
            elif opt[0] == "-r" or opt[0] == "--reverse":
                reverse = True
            elif opt[0] == "-y":
                kwargs["yes"] = True
            else:
                raise Exception("Unknown option %s=%s" % (opt[0], opt[1]))

        if reverse:
            main(dst, src, **kwargs)
        else:
            main(src, dst, **kwargs)

    except Exception as e:
        sys.stderr.write("ERROR: %s\n" % str(e))
        raise SystemExit(-1)

