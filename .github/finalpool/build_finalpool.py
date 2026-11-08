import json, subprocess, sys, pathlib
manifest_path, out_dir = sys.argv[1], sys.argv[2]
manifest = json.loads(pathlib.Path(manifest_path).read_text())
out = pathlib.Path(out_dir)
if out.exists():
    import shutil; shutil.rmtree(out)
out.mkdir(parents=True)
total = 0
for item in manifest:
    branch = item['branch']; src = item['source']; name = item['name']
    ref = 'origin/' + branch
    files = subprocess.check_output(['git','ls-tree','-r','--name-only',ref,src], text=True).splitlines()
    if not files:
        raise SystemExit(f'No files for {name} on {ref}')
    for f in files:
        if not f.startswith(src):
            raise SystemExit(f'Unexpected path {f} for {src}')
        rel = f[len(src):]
        data = subprocess.check_output(['git','show',f'{ref}:{f}'])
        target = out / name / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        total += 1
    for required in ['docs/task.md','evaluation/main.py']:
        if not (out / name / required).is_file():
            raise SystemExit(f'{name} missing {required}')
print(f'Built {len(manifest)} tasks, {total} files')
