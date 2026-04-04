# pipeline_data_slv

Build the image:

```bash
sudo docker build --tag gee-test .
```

To test the built image, we can try executing it with ```docker run```:

```bash
sudo docker run  --network host gee-test:latest
```