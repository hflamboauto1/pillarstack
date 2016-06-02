# top level pillar customer abscract config.
# Status: Prototype, not functionnal
#
# See customers.d/ for details on each customer
# See also: base/customers/init.sls for state.
#
#
wsf:
  customers:
    # list elements will be used for naming users (shell, db)
    client1:
      domain-name: client1-domain.fr
      enabled: true
      delete: false
      # service to configure for this customer
      services:
        - webhost
        - dns
        - mysql
        - sftp
      # some service override…
      override:
        user-shell:
          name: test
        php-fpm:
          user:
            name: test
            group: test
          pool:
            pm: dynamic
            pm.max_children: 7
            pm.start_servers: 3
            pm.min_spare_servers: 1
            pm.max_spare_servers: 3
            pm.process_idle_timeout: 30s
            pm.max_requests: 100
    # client2 as more default values
    client2:
      domain-name: more-domain.com
      enabled: true
      delete: false
      services:
        - webhost
        - dns
    client3:
      domain-name: somedomain.fr
      enabled: true
      # default, delete: false
      services:
        - webhost
        - dns
        - db
        - sftp

