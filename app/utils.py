import trafaret as t
import yaml
import pathlib

PROJ_ROOT = pathlib.Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = PROJ_ROOT / 'config' / 'config.yml'

CONFIG_TRAFARET = t.Dict(
    {
        'host': t.IP,
        'port': t.Int(),
        t.Key('mysql'): t.Dict(
            {
                'database': t.String(),
                'user': t.String(),
                'password': t.String(),
                'host': t.String(),
                'port': t.Int()
            }
        ),
    }
)


def load_config(fname):
    with open(fname, 'rt') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return CONFIG_TRAFARET.check(data)