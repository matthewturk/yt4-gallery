import click
import yaml
import sys
import os
import json
import requests

YT3_PATH = os.path.expanduser("~/yt/yt-3.x-clean/")
YT4_PATH = os.path.expanduser("~/yt/yt/")

field_spec = yaml.load(open("field_spec.yaml"), Loader = yaml.SafeLoader)

def _get_datafiles():
    datafiles = json.loads(requests.get('https://yt-project.org/data/datafiles.json').content)
    return datafiles

@click.group()
def main():
    pass

@main.command()
def list_datafiles():
    d = _get_datafiles()
    for frontend in sorted(d):
        for ds in sorted(d[frontend], key = lambda a: a['filename']):
            click.echo(f"{frontend}/{ds['filename']}")

def append_saved_file(dataset, version, plot_index, info):
    if os.path.isfile("catalog.json"):
        current = json.load(open("catalog.json", "r"))
    else:
        current = {}
    current.setdefault(dataset, {}).setdefault(version, {})[plot_index] = info
    json.dump(current, open("catalog.json", "w"))

@main.command()
@click.option("-y", "--yt-version", required=False, default=4, type=int)
@click.argument("dataset", type=str, required=True)
def make_plots(dataset, yt_version):
    if yt_version == 3:
        sys.path.insert(0, YT3_PATH)
        field_key = 'yt3'
        weight_default = ("deposit", "gas_density")
    elif yt_version == 4:
        sys.path.insert(0, YT4_PATH)
        field_key = 'yt4'
        weight_default = ("gas", "density")
    else:
        raise click.BadParameter('yt version must be 3 or 4')
    import yt
    click.echo(yt)
    ds = yt.load_sample(dataset)
    click.echo(ds)
    os.makedirs(dataset, exist_ok = True)
    plot_index = 0
    for field in field_spec['fields']:
        f = tuple(field[field_key])
        weights = [weight_default]
        if field['weight_none']:
            weights.append(None)
        for weight in weights:
            if weight is not None:
                w = tuple(weight)
                wn = f"{w[1]}"
            else:
                w = None
                wn = "None"
            for ax in field_spec['axis']:
                p = yt.ProjectionPlot(ds, ax, f, weight_field = w)
                for zoom in field_spec['zoom']:
                    p.set_width(1.0, 'unitary')
                    p.zoom(zoom)
                    fn = f"{dataset}/yt{yt_version}_p{plot_index:04d}_proj_{f[1]}_{wn}_{ax}_z{zoom:03d}.png"
                    click.echo(f"Saving {fn}")
                    p.save(fn)
                    plot_index += 1
                    append_saved_file(dataset, f"yt{yt_version}", plot_index,
                                      {'field': f, 'axis': ax, 'weight_field': w,
                                       'zoom': zoom, 'filename': fn})

if __name__ == "__main__":
    sys.exit(main())
