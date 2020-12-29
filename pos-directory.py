import pathlib
from datetime import datetime
import glob
import os
import sys
import actibpos
from multiprocessing import Pool

if len(sys.argv) < 2:
    print("error: you must pass a directory as argument to the script")
    sys.exit(1)

indir = sys.argv[1]

now = datetime.now()
dt = now.strftime("%Y%m%d_%H-%M-%S")

segoutpath = pathlib.Path("output-"+dt+"/seg/")
posoutpath = pathlib.Path("output-"+dt+"/pos/")
segoutpath.mkdir(parents=True, exist_ok=True)
posoutpath.mkdir(parents=True, exist_ok=True)

POOL = Pool(processes=3)  

def main():
    filenames = pathlib.Path(indir).rglob('*.xml')
    for filename in sorted(filenames, key=lambda fn: str(fn)):
        print("treating %s" % filename)
        basename = os.path.basename(filename)
        if basename.startswith("_"):
            continue
        noext = os.path.splitext(basename)[0]
        posoutfilename = os.path.join(posoutpath, noext+".txt")
        segoutfilename = os.path.join(segoutpath, noext+".txt")
        print("apply_async")
        POOL.apply_async(actibpos.processfiles, args=(filename, segoutfilename, posoutfilename, "seg:pos", "bdrc-tei"))

    filenames = pathlib.Path(indir).rglob('*.txt')
    for filename in sorted(filenames, key=lambda fn: str(fn)):
        print("treating %s" % filename)
        basename = os.path.basename(filename)
        if basename.startswith("_"):
            continue
        noext = os.path.splitext(basename)[0]
        posoutfilename = os.path.join(posoutpath, noext+".txt")
        segoutfilename = os.path.join(segoutpath, noext+".txt")
        POOL.apply_async(actibpos.processfiles, args=(filename, segoutfilename, posoutfilename, "seg:pos", "txt"))
    POOL.close()
    POOL.join()

main()