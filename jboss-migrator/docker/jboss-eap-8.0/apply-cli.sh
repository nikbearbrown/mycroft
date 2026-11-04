#!/usr/bin/env bash
# Applies generated JBoss CLI scripts to an embedded (offline) server, then deploys the artifact.
set -euo pipefail

for script in /tmp/staging/*.cli; do
  [ -e "$script" ] || continue
  echo "applying $script"
  {
    echo "embed-server --server-config=standalone.xml --std-out=echo"
    cat "$script"
    echo "stop-embedded-server"
  } > /tmp/run.cli
  "$JBOSS_HOME/bin/jboss-cli.sh" --file=/tmp/run.cli
done

cp /tmp/staging/*.war /tmp/staging/*.ear "$JBOSS_HOME/standalone/deployments/" 2>/dev/null || true
ls "$JBOSS_HOME/standalone/deployments/"
