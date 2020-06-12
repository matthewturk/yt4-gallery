import json
import os
import yt
import contextlib
import time

@contextlib.contextmanager
def timing(name):
    print(f"Requested for {name}")
    t1 = time.time()
    v = {}
    yield v
    t2 = time.time()
    i = info.setdefault(name, {'values': [], 'times': []})
    print(f"Appending {t2-t1} => {v['value']}")
    i['times'].append(t2-t1)
    i['values'].append(v['value'])

os.chdir("OUTPUT_DIRECTORY")

info = {}

print("LOADING SAMPLE_FILENAME")
ds = yt.load_sample("SAMPLE_FILENAME")

ds.index

field_spec = [ (("gas", "density"), ("gas", "density")),
               (("gas", "temperature"), ("gas", "density")),
               (("gas", "density"), None) ]

with timing("find_max") as v:
    x, y, z = ds.r[:].argmax( ("gas", "density") )
    v['value'] = "%s %s %s" % (x, y, z)
    print(v['value'])

for field in field_spec:
    for ax in 'xyz':
        with timing("projection") as v:
            p = yt.ProjectionPlot(ds, ax, field[0], weight_field=field[1])#, center = (x, y, z))
            v['value'] = p.save()[0]

json.dump(info, open("info.json", "w"), indent=2)
