%global name emdad
%global release 1
%global unmangled_version %{version}
%global __requires_exclude ^.*emdad/addons/mail/static/scripts/emdad-mailgate.py$

Summary: emdad Server
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: LGPL-3
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: emdad S.A. <info@emdad.com>
Requires: sassc
BuildRequires: python3-devel
BuildRequires: pyproject-rpm-macros
Url: https://www.emdad.com

%description
emdad is a complete ERP and CRM. The main features are accounting (analytic
and financial), stock management, sales and purchases management, tasks
automation, marketing campaigns, help desk, POS, etc. Technical features include
a distributed server, an object database, a dynamic GUI,
customizable reports, and XML-RPC interfaces.

%generate_buildrequires
%pyproject_buildrequires

%prep
%autosetup

%build
%py3_build

%install
%py3_install

%post
#!/bin/sh

set -e

emdad_CONFIGURATION_DIR=/etc/emdad
emdad_CONFIGURATION_FILE=$emdad_CONFIGURATION_DIR/emdad.conf
emdad_DATA_DIR=/var/lib/emdad
emdad_GROUP="emdad"
emdad_LOG_DIR=/var/log/emdad
emdad_LOG_FILE=$emdad_LOG_DIR/emdad-server.log
emdad_USER="emdad"

if ! getent passwd | grep -q "^emdad:"; then
    groupadd $emdad_GROUP
    adduser --system --no-create-home $emdad_USER -g $emdad_GROUP
fi
# Register "$emdad_USER" as a postgres user with "Create DB" role attribute
su - postgres -c "createuser -d -R -S $emdad_USER" 2> /dev/null || true
# Configuration file
mkdir -p $emdad_CONFIGURATION_DIR
# can't copy debian config-file as addons_path is not the same
if [ ! -f $emdad_CONFIGURATION_FILE ]
then
    echo "[options]
; This is the password that allows database operations:
; admin_passwd = admin
db_host = False
db_port = False
db_user = $emdad_USER
db_password = False
addons_path = %{python3_sitelib}/emdad/addons
default_productivity_apps = True
" > $emdad_CONFIGURATION_FILE
    chown $emdad_USER:$emdad_GROUP $emdad_CONFIGURATION_FILE
    chmod 0640 $emdad_CONFIGURATION_FILE
fi
# Log
mkdir -p $emdad_LOG_DIR
chown $emdad_USER:$emdad_GROUP $emdad_LOG_DIR
chmod 0750 $emdad_LOG_DIR
# Data dir
mkdir -p $emdad_DATA_DIR
chown $emdad_USER:$emdad_GROUP $emdad_DATA_DIR

INIT_FILE=/lib/systemd/system/emdad.service
touch $INIT_FILE
chmod 0700 $INIT_FILE
cat << EOF > $INIT_FILE
[Unit]
Description=emdad Open Source ERP and CRM
After=network.target

[Service]
Type=simple
User=emdad
Group=emdad
ExecStart=/usr/bin/emdad --config $emdad_CONFIGURATION_FILE --logfile $emdad_LOG_FILE
KillMode=mixed

[Install]
WantedBy=multi-user.target
EOF


%files
%{_bindir}/emdad
%{python3_sitelib}/%{name}-*.egg-info
%{python3_sitelib}/%{name}
