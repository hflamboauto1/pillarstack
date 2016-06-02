# process customers in customers.sls pillar
#
# !! Warning: this is a state which create pillar for other states
#
# generated files are in the pillar and must be reviewed by the admin
# before applying any other state
#
# Usage:
# (on the saltmaster)
#   salt-call state.apply customers
#   cd target_dir
#   git diff # double check
#   salt '*' saltutils.pillar_refresh # propagate changes
#
# after…
#   salt 'db*' config.get mysql:user # tripple check from a db server
#   salt 'db*' state.apply mysql.user # update users
# commit changes:
#   cd target_dir
#   git commit -a

# target folder for generated pillar
{% set pillar_dir = '/srv/salt/pillar' -%}
{% set target_dir = pillar_dir + '/auto' -%}
{{ target_dir }}:
  file.directory:
    - user: root
    - group: root
    - dir_mode: 755

# produce managed databases for customers in pillar/customers
{{ target_dir }}/mysql_db.sls:
  file.managed:
    - source: salt://customers/templates/databases.sls
    - user: root
    - group: root
    - mode: 644
    - template: jinja

# generate password for customers
{%  set password_db = target_dir + '/managed_password.yaml' -%}
{%  set user_db = pillar_dir + '/customers.sls' -%}
check_passwords:
  cmd.run:
    - name: ./customers_passwords.py {{ user_db }} {{ password_db }}
    - cwd: /srv/salt/base/customers

# just ensure restricted permissions
generate_customers_passwords:
  file.managed:
    - name: {{ password_db }}
    - user: root
    - group: root
    - mode: 600

# produce managed databases for customers in pillar/customers
{{ target_dir }}/mysql_users.sls:
  file.managed:
    - source: salt://customers/templates/mysql_users.sls
    - user: root
    - group: root
    - mode: 644
    - template: jinja
    - defaults:
       password_db: {{ password_db }}
