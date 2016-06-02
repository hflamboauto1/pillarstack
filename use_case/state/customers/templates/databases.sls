{# vim: set ft=jinja: -#}
#
# DON'T EDIT THIS FILE: salt managed file
#
mysql:
  # Managed databases for customers
  database:
{%- for name, client in salt['pillar.get']('wsf:customers', {}).items() %}
    - {{ name -}}
{% endfor %}
