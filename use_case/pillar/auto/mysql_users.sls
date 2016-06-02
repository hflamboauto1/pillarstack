# vim: set ft=jinja:
#
# DON'T EDIT THIS FILE: salt managed file
#
{% import_yaml "/srv/salt/pillar/auto/managed_password.yaml" as pass with context %}
mysql:
  # Managed mariaDB users for customers
  user:

    client1:
      password: "{{ pass['client1']['mysql'] }}"
      hosts:
        - localhost
      databases:
        - database: client1
          grants: ['all privileges']

    client2:
      password: "{{ pass['client2']['mysql'] }}"
      hosts:
        - localhost
      databases:
        - database: client2
          grants: ['all privileges']

    client3:
      password: "{{ pass['client3']['mysql'] }}"
      hosts:
        - localhost
      databases:
        - database: client3
          grants: ['all privileges']

