#!/bin/bash
if [ -z "$1" ]; then
    echo "参数为空，请提供有效参数。"
    exit 1
fi

HOST=$1
ansible $1 -m ping -i /etc/kolla/hosts
ansible $1 -b -m reboot -i /etc/kolla/hosts 
sleep 10
ansible $1 -m ping -o --become --become-method=sudo -a 'data="until ping -c1 your_host &>/dev/null; do sleep 1; done"' -i /etc/kolla/hosts
#ansible $1 -m ping -i /etc/kolla/hosts
ansible $1 -m command -a "ip a" -i /etc/kolla/hosts


