#!/bin/bash
set -x

# Init the arguments
ADMIN_TOKEN=${ADMIN_TOKEN:-294a4c8a8a475f9b9836}
ADMIN_TENANT_NAME=${ADMIN_TENANT_NAME:-admin}
ADMIN_USER_NAME=${ADMIN_USERNAME:-admin}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-ADMIN_PASS}
ADMIN_EMAIL=${ADMIN_EMAIL:-${ADMIN_USER_NAME}@example.com}

OS_TOKEN=$ADMIN_TOKEN
OS_URL=${OS_AUTH_URL:-"http://${HOSTNAME}:35357/v3"}
OS_IDENTITY_API_VERSION=3

CONFIG_FILE=/etc/keystone/keystone.conf
SQL_SCRIPT=${SQL_SCRIPT:-/root/keystone.sql}

if env | grep -qi MYSQL_ROOT_PASSWORD && test -e $SQL_SCRIPT; then
    MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-$MYSQL_ENV_MYSQL_ROOT_PASSWORD}
    MYSQL_HOST=${MYSQL_HOST:-mysql}
    sed -i "s#^connection.*=.*#connection = mysql://keystone:KEYSTONE_DBPASS@${MYSQL_HOST}/keystone#" $CONFIG_FILE
    mysql -uroot -p$MYSQL_ROOT_PASSWORD -h $MYSQL_HOST <$SQL_SCRIPT
fi

rm -f $SQL_SCRIPT

# update keystone.conf
sed -i "s#^admin_token.*=.*#admin_token = $ADMIN_TOKEN#" $CONFIG_FILE

# Populate the Identity service database
keystone-manage db_sync
# Initialize Fernet keys
keystone-manage fernet_setup --keystone-user root --keystone-group root
mv /etc/keystone/default_catalog.templates /etc/keystone/default_catalog

# start keystone service
uwsgi --http 0.0.0.0:35357 --wsgi-file $(which keystone-wsgi-admin) &
# uwsgi --http 0.0.0.0:5000 --wsgi-file $(which keystone-wsgi-public) &
sleep 5 # wait for start

export OS_TOKEN OS_URL OS_IDENTITY_API_VERSION

# Initialize account
openstack service create  --name keystone identity
openstack endpoint create --region RegionOne identity public http://${HOSTNAME}:5000/v3
openstack endpoint create --region RegionOne identity internal http://${HOSTNAME}:5000/v3
openstack endpoint create --region RegionOne identity admin http://${HOSTNAME}:5000/v3
openstack domain create --description "Default Domain" default
openstack project create --domain default  --description "Admin Project" admin
openstack user create --domain default --password $ADMIN_PASSWORD admin
openstack role create admin
openstack role create users
openstack role add --project admin --user admin admin

openstack user create --domain default --password root root
openstack user create --domain default --password user user1
openstack user create --domain default --password user user2
openstack user create --domain default --password user3 user3
openstack role add --project admin --user root users
openstack role add --project admin --user user1 users
openstack role add --project admin --user user2 users
openstack role add --project admin --user user3 users

unset OS_TOKEN OS_URL

# Write openrc to disk
cat >~/openrc <<EOF
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=${ADMIN_PASSWORD}
export OS_AUTH_URL=http://${HOSTNAME}:35357/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
EOF

cat ~/openrc

# reboot services
pkill uwsgi
sleep 5
uwsgi --http 0.0.0.0:5000 --wsgi-file $(which keystone-wsgi-public) &
sleep 5
uwsgi --http 0.0.0.0:35357 --wsgi-file $(which keystone-wsgi-admin)
