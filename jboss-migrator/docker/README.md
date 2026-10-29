# Verification images

`migrator/verify/deploy.py` builds `docker/<server>/Dockerfile`, where `<server>` is
`source.server` / `target.server` from `migration.yaml`. Before each build it copies the packaged
WAR/EAR and the generated `migration/jboss-cli/*.cli` scripts into `docker/<server>/staging/`.

- `jboss-eap-7.2/`: baseline (source) server, used for the "before" screenshots
- `jboss-eap-8.0/`: target server; applies the CLI scripts offline with an embedded server, then deploys

The Red Hat images need `docker login registry.redhat.io`. Each Dockerfile names the WildFly
image to use instead if you don't have a subscription. To support another target (for example
`wildfly-31`), add a folder with that name.

Datasource scripts read `DB_URL`, `DB_USER`, `DB_PASSWORD` and `DB_DRIVER` from the container
environment. Point them at a disposable database seeded the same way for the baseline and target
runs, so the screenshots are comparable.
