## Image creation
Build the image:

```bash
sudo docker build --tag models-test .
```

To test the built image, we can try executing it with ```docker run```:

```bash
sudo docker run  --network host models-test:latest
```
