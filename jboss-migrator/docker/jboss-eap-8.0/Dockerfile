# Target server for verification. Requires `docker login registry.redhat.io`.
# Without a Red Hat subscription, use the WildFly equivalent:
#   FROM quay.io/wildfly/wildfly:31.0.1.Final-jdk17
FROM registry.redhat.io/jboss-eap-8/eap8-openjdk17-builder-openshift-rhel8:latest

USER root
COPY staging/ /tmp/staging/
COPY apply-cli.sh /tmp/apply-cli.sh
RUN bash /tmp/apply-cli.sh && chown -R jboss:root "$JBOSS_HOME/standalone"
USER jboss

EXPOSE 8080
CMD ["/bin/sh", "-c", "$JBOSS_HOME/bin/standalone.sh -b 0.0.0.0"]
