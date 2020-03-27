You can run the following to "upgrade" a config file easily.
Note: This may cause problems, but it's the easiest thing to do.
Also, this seems to work to move a config file from a newer kernel to an older kernel, too.

```
cp <old config> .config
yes '' | make oldconfig
```
