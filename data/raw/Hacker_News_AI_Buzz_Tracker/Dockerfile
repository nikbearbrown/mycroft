# The n8n image is now a Docker Hardened Image (DHI): Alpine-based, but the
# `apk` package manager binary is stripped out (so `apk add` fails with exit
# 127, "command not found"), and its package DB pins versions that conflict
# with a plain `apk add`.
#
# Instead of running apk inside the hardened image, we install Python and its
# full dependency closure into a staging root in a matching stock Alpine
# builder, then copy that tree into the final image.
FROM alpine:3.22 AS pybuild

# --initdb sets up a fresh apk database under /staging so the whole runtime
# dependency closure (libssl, libffi, sqlite, ...) lands in one tree.
RUN apk add --no-cache --initdb --root /staging \
        --repositories-file /etc/apk/repositories \
        --keys-dir /etc/apk/keys \
        python3 py3-pip

FROM docker.n8n.io/n8nio/n8n:latest

USER root

# Overlay Python + its shared libraries onto the n8n image. Both stages are
# Alpine 3.22, so the libraries are ABI-compatible with n8n's existing ones.
COPY --from=pybuild /staging/usr /usr
COPY --from=pybuild /staging/lib /lib
COPY --from=pybuild /staging/etc/ssl /etc/ssl

# Make `python` available alongside `python3`.
RUN ln -sf /usr/bin/python3 /usr/local/bin/python

USER node
