#!/bin/sh

{

set -e

echo $DO_LOCAL_CONFIG

until PGPASSWORD=do_portal psql -h db -U do_portal -c '\q'; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - check schema"

# DB init
if PGPASSWORD=do_portal psql -U do_portal -h cert_db -d do_portal -lqt | cut -d \| -f 1 | grep -qw do_portal; then
  echo '###############'
  echo '### init DB ###'
  echo '###############'
  source bin/activate
  echo '### dropdb'
  PGPASSWORD=do_portal dropdb -U do_portal -h cert_db do_portal;
  echo '### createdb'
  PGPASSWORD=do_portal createdb -U do_portal -h cert_db -O do_portal do_portal;
  mv misc/migrations misc/tmp-migrations # TODO remove hack
  echo '### init'
  python3 manage.py db init;
  echo '### migrate'
  python3 manage.py db migrate;
  echo '### upgrade'
  python3 manage.py db upgrade;
  echo '### initializedb'
  python3 manage.py initializedb;
  echo '### insertmasteruser'
  python3 manage.py insertmasteruser;
  echo '### addyaml'
  python3 demodata.py addyaml
  rm -rf misc/migrations # TODO remove hack
  mv misc/tmp-migrations misc/migrations # TODO remove hack

  echo '### init RIPE/FODY'
  # pg_dump --no-owner --schema-only --no-privileges contactdb > /tmp/contactdb_schema_only.pgdump
  PGPASSWORD=do_portal psql -h db -U do_portal -c "CREATE SCHEMA fody";
  PGPASSWORD=do_portal psql -U do_portal -h cert_db -d do_portal --echo-errors --file=install/contactdb_schema_only.pgdump
fi

source ./bin/activate && python manage.py run -h 0.0.0.0 -p 5001

} >&2 # redirect stout to stderr
