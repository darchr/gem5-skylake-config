# gem5art-template

This is a template for setting up a gem5art experiment.
A typical gem5art experiment includes:
* disk-image: (requires for full system runs) contains all relevant scripts to generate disk images and the images themselves.
* gem5-configs: contains gem5 configs.
* linux-configs: (requires for full system runs) contains Linux configs used for generating Linux kernel.
* results: contains the experiment's results.
* A launch script. `launch_boot_tests.py` is an example launch script used in boot-test experiment.

To install gem5art,
```sh
pip install gem5art-artifact gem5art-run gem5art-tasks
```

[More details about gem5art](https://github.com/darchr/gem5art).

Additional steps to launch the experiment could be found [here](https://gem5art.readthedocs.io/en/latest/tutorials/boot-tutorial.html).
