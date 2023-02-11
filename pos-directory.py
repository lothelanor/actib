import pathlib
from datetime import datetime
import glob
import os
import sys
import actibpos
from multiprocessing import Pool, freeze_support

if len(sys.argv) < 2:
    print("error: you must pass a directory as argument to the script")
    sys.exit(1)

indir = sys.argv[1]
if indir.endswith("/"):
    indir = indir[:-1]

previousdir = pathlib.Path("output-20200712_14-12-35")

def main():
    POOL = Pool(processes=5)

    now = datetime.now()
    dt = now.strftime("%d%m%Y_%H-%M-%S")

    segoutpath = pathlib.Path(indir+"-out-"+dt+"/seg/")
    posoutpath = pathlib.Path(indir+"-out-"+dt+"/pos/")
    pyrrhaoutpath = pathlib.Path(indir+"-out-"+dt+"/pyrrha/")
    segoutpath.mkdir(parents=True, exist_ok=True)
    posoutpath.mkdir(parents=True, exist_ok=True)
    pyrrhaoutpath.mkdir(parents=True, exist_ok=True)
    
    filenames = pathlib.Path(indir).rglob('*.xml')
    for filename in sorted(filenames, key=lambda fn: str(fn)):
        print("treating %s" % filename)
        basename = os.path.basename(filename)
        if basename.startswith("_"):
            continue
        noext = os.path.splitext(basename)[0]
        posoutfilename = os.path.join(posoutpath, noext+".txt")
#        pyrrhaposoutfilename = os.path.join(pyrrhaposoutpath, noext+".txt")
        segoutfilename = os.path.join(segoutpath, noext+".txt")
        if previousdir is not None and (previousdir/"pos"/(noext+".txt")).is_file():
            print("skipping "+noext)
            continue
        POOL.apply_async(actibpos.processfiles, args=(filename, segoutfilename, posoutfilename, pyrrhaoutfilename, "seg:pos", "bdrc-tei"))

    filenames = pathlib.Path(indir).rglob('*.txt')
    for filename in sorted(filenames, key=lambda fn: str(fn)):
        print("treating %s" % filename)
        basename = os.path.basename(filename)
        if basename.startswith("_"):
            continue
        noext = os.path.splitext(basename)[0]
        posoutfilename = os.path.join(posoutpath, noext+".txt")
        pyrrhaoutfilename = os.path.join(pyrrhaoutpath, noext+".txt")
        segoutfilename = os.path.join(segoutpath, noext+".txt")
        if previousdir is not None and (previousdir/"seg"/(noext+".txt")).is_file():
            print("skipping "+noext)
            continue
        POOL.apply_async(actibpos.processfiles, args=(filename, segoutfilename, posoutfilename, pyrrhaoutfilename, "seg:pos", "txt"))
    POOL.close()
    POOL.join()

if __name__ == '__main__':
    freeze_support()
    main()