
FROM gramineproject/gramine

RUN apt update

RUN apt install build-essential -y

WORKDIR /root

# COPY ./dafny /usr/lib/dafny
COPY ./dafny /root/dafny
COPY ./scripts /root/scripts
COPY ./Makefile /root/Makefile
# COPY ./docker-setup.sh /root/setup.sh
COPY ./dafny.manifest.template /root/dafny.manifest.template
COPY ./key/enclave-key.pem /root/.config/gramine/enclave-key.pem

RUN make build

# COPY ./scripts /root/scripts
ENTRYPOINT [ "gramine-sgx", "dafny", "/version" ]
# ENTRYPOINT [ "gramine-sgx", "dafny", "scripts/Abs.dfy" ]
