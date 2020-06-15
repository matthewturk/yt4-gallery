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
    #datafiles = json.loads(requests.get('https://yt-project.org/data/datafiles.json').content)
    datafiles = json.load(open("sample_data_registry.json"))
    return datafiles

@click.group()
def main():
    pass

@main.command()
def list_datafiles():
    d = _get_datafiles()
    for ds in sorted(d):
        if ds.endswith(".tar.gz"):
            fn = ds[:-7]
        else:
            fn = ds
        click.echo(f"{fn}");

def append_saved_file(dataset, version, info):
    if os.path.isfile("catalog.json"):
        current = json.load(open("catalog.json", "r"))
    else:
        current = {}
    current.setdefault(dataset, {}).setdefault(version, []).append(info)
    json.dump(current, open("catalog.json", "w"))

@main.command()
@click.option("-y", "--yt-version", required=False, default=4, type=int)
@click.argument("dataset", type=str, required=True)
def make_plots(dataset, yt_version):
    if yt_version == 3:
        sys.path.insert(0, YT3_PATH)
        field_key = 'yt4'
        #weight_default = ("deposit", "gas_density")
        weight_default = ("gas", "density")
        import yt
        catalog = _get_datafiles()
        ds = yt.load(f"{dataset}.tar.gz.untar/{dataset}/{catalog[dataset + '.tar.gz']['load_name']}")
    elif yt_version == 4:
        sys.path.insert(0, YT4_PATH)
        field_key = 'yt4'
        weight_default = ("gas", "density")
        import yt
        click.echo(yt)
        ds = yt.load_sample(dataset)
    else:
        raise click.BadParameter('yt version must be 3 or 4')
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
                    p.set_cmap("all", field['colormap'])
                    fn = f"{dataset}/yt{yt_version}_p{plot_index:04d}_proj_{f[1]}_{wn}_{ax}_z{zoom:03d}.png"
                    click.echo(f"Saving {fn}")
                    p.save(fn)
                    append_saved_file(dataset, f"yt{yt_version}", 
                                      {'field_key': f"{f[1]}_{wn}", 'axis': ax, 
                                       'zoom': zoom, 'filename': fn,
                                       'plot_index': plot_index})
                    plot_index += 1

if __name__ == "__main__":
    sys.exit(main())
