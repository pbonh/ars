regenerate-ignition-file:
  rm -f ignition/pbonh.ign
  podman run --interactive --rm --security-opt label=disable \
       --volume "${PWD}:/pwd" --workdir /pwd quay.io/coreos/butane:release \
       --pretty --strict ignition/pbonh.bu > ignition/pbonh.ign
