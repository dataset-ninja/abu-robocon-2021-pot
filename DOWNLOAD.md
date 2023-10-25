Dataset **ABU Robocon 2021 Pot** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/supervisely-supervisely-assets-public/teams_storage/k/x/h1/jrDwnWGsrgA3ArIj2sMU8KBAztcEn17C3Iqe14J9ovaGJjJsHIvL1Gc8zmWOhWRCtxUvbkpy6eq1DIWY3ydgn4bU59lCBRQUYNRiwM8EL5i2johT5FD6f3VaCb5p.tar)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='ABU Robocon 2021 Pot', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

