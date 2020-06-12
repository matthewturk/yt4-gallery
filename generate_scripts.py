import os
import os
import yt
import json
import requests

yt4_template = open("yt4_script.tmpl.py", "r").read()

def write_script(d):
    base_dir = os.path.join(d['code'], d['filename'])
    base_dir = base_dir.replace("(", "").replace(")", "").replace(" ", "_")
    os.makedirs(base_dir, exist_ok=True)
    print(base_dir)
    with open(os.path.join(base_dir, "generation_script.py"), "w") as f:
        v = (yt4_template.replace("SAMPLE_FILENAME", d['filename'])
                         .replace("OUTPUT_DIRECTORY", base_dir))
        f.write(v)

frontends = ["arepo", "sph"]

datafiles = json.loads(requests.get('https://yt-project.org/data/datafiles.json').content)

for frontend in frontends:
    df = datafiles[frontend + " frontend"]
    for d in df:
        #ds = yt.load_sample(d['filename'])
        write_script(d)


