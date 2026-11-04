# Source server for baseline UI snapshots. Requires `docker login registry.redhat.io`.
# Without a Red Hat subscription, use the WildFly equivalent:
#   FROM quay.io/wildfly/wildfly:14.0.1.Final
FROM registry.redhat.io/jboss-eap-7/eap72-openshift:latest

USER root
COPY staging/ /tmp/staging/
RUN cp /tmp/staging/*.war /tmp/staging/*.ear "$JBOSS_HOME/standalone/deployments/" 2>/dev/null || true \
 && chown -R jboss:root "$JBOSS_HOME/standalone"
USER jboss

EXPOSE 8080
CMD ["/bin/sh", "-c", "$JBOSS_HOME/bin/standalone.sh -b 0.0.0.0"]
