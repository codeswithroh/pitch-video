#!/usr/bin/env python3
"""Step 11: clean up. Run in the work dir after verify passed and the file was delivered.

Moves the finished videos (project.json "output", its _small copy and, for a pitch video, the _vertical cut)
to the top of the work dir and deletes everything else: source.mov, cuts, stems, overlays, logs, renders.

  clean.py                  delete (asks for nothing; refuses unless verify.py passed on the current output)
  clean.py --dry-run        list what would go and what stays
  clean.py --keep take.mov  keep more paths (the user's own take, if it sits in the work dir)
"""
import argparse, json, os, shutil, sys

ap = argparse.ArgumentParser()
ap.add_argument("--dry-run", action="store_true")
ap.add_argument("--keep", nargs="*", default=[])
ap.add_argument("--force", action="store_true", help="clean even without a verify pass")
a = ap.parse_args()

work = os.path.abspath(".")
if not os.path.exists("project.json"): sys.exit("not a pitch-video work dir (no project.json): nothing deleted")
if work == os.path.expanduser("~") or os.path.exists(".git"):
    sys.exit("this looks like a home or project folder, not a work dir: nothing deleted")
out = json.load(open("project.json")).get("output", "out/demo.mp4")
cands = [out, out.replace(".mp4", "_small.mp4"), out.replace(".mp4", "_vertical.mp4"), out.replace(".mp4", "_vertical_small.mp4")]
videos = [p for p in cands if os.path.isfile(p)]
if not os.path.isfile(out): sys.exit(f"{out} is missing: nothing deleted")
mark = os.path.join(os.path.dirname(out) or ".", ".verified")
if not a.force and not (os.path.exists(mark) and open(mark).read().strip() == str(int(os.path.getmtime(out)))):
    sys.exit("verify.py has not passed on the current output: run it first (or --force). Nothing deleted")

stay = {os.path.basename(p) for p in videos} | {os.path.normpath(k).split(os.sep)[0] for k in a.keep}
if len({os.path.basename(p) for p in videos}) < len(videos): sys.exit("two outputs share a file name: nothing deleted")
for p in videos:
    print(f"keep  {os.path.basename(p)}")
    if not a.dry_run and os.path.dirname(os.path.abspath(p)) != work: shutil.move(p, os.path.basename(p))
for k in sorted(a.keep): print(f"keep  {k}")
gone = 0
for name in sorted(os.listdir(".")):
    if name in stay: continue
    print(f"{'would delete' if a.dry_run else 'delete'}  {name}")
    if not a.dry_run:
        shutil.rmtree(name) if os.path.isdir(name) and not os.path.islink(name) else os.remove(name)
    gone += 1
print(f"{'would delete' if a.dry_run else 'deleted'} {gone} items; left: {', '.join(sorted(stay))}")
