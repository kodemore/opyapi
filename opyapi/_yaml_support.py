from yaml import FullLoader as YamlFullLoader, load as load_yaml
from functools import partial

load_yaml = partial(load_yaml, Loader=YamlFullLoader)
