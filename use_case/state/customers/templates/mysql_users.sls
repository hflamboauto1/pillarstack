# vim: set ft=jinja:
#
# DON'T EDIT THIS FILE: salt managed file
#
{# will import on the pillar side a generated passwords database -#}
{{ '{%' }} import_yaml "{{ password_db }}" as pass with context {{ '%}' }}
mysql:
  # Managed mariaDB users for customers
  user:
{% set db_server = 'localhost' -%}
{%- for name, prop in salt['pillar.get']('wsf:customers', {}).items() %}
    {{ name }}:
      password: {{ '"{{' }} pass['{{ name }}']['mysql'] {{ '}}"' }}
      hosts:
        - {{ db_server }}
      databases:
        - database: {{ name }}
          grants: ['all privileges']
{% endfor -%}
