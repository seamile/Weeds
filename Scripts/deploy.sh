#!/bin/bash
#
#   线上环境部署脚本
#
#   Auth: Seamile   Version: 0.1
#   Date: 2011-08-08
#
#   使用说明：
#       针对不同环境，执行结尾 main 函数中的方法，不需要的注释掉


mkdir -p /root/backup
BACKUP_DIR=/root/backup
DOWNLOAD_SERVER='http://10.0.0.1:3000'
DOWNLOAD_DIR=/usr/local/src/
LOG=`pwd`/SETUP_LOG_`date +"%Y-%m-%d_%H:%M:%S"`


####################################################
###                  基础环境搭建                  ###
####################################################


# 修改文件描述符
set_ulimit()
{
echo "Doing $FUNCNAME..."
cp -n /etc/security/limits.conf $BACKUP_DIR/etc-security-limits.conf
cat >> /etc/security/limits.conf <<EOF
* soft nofile 32768
* hard nofile 65536
EOF
echo -e "Done $FUNCNAME\n"
}


# 设置内核参数
set_kernel()
{
echo "Doing $FUNCNAME..."
sysctl -a > $BACKUP_DIR/etc-sysctl.conf.all
cp -n /etc/sysctl.conf $BACKUP_DIR/etc-sysctl.conf
cat >> /etc/sysctl.conf <<EOF
net.core.somaxconn = 262144
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_fin_timeout = 3
net.ipv4.tcp_keepalive_time = 60
net.ipv4.tcp_max_orphans = 131072
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_sack = 1
net.ipv4.tcp_fack = 1
net.core.netdev_max_backlog = 8192
net.ipv4.tcp_max_syn_backlog = 262144
net.ipv4.tcp_no_metrics_save = 1
net.ipv4.tcp_syn_retries = 1
net.ipv4.tcp_synack_retries = 1
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_tw_buckets = 6000
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_tw_recycle = 0
net.ipv4.tcp_tw_reuse = 1
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_mem = 1549137 2065518 3098274
net.ipv4.tcp_rmem =   4096   87380 6291456
net.ipv4.tcp_wmem =   4096   16384 4194304
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1
EOF
sysctl -p >> $LOG
echo -e "Done $FUNCNAME\n"
}


# 关闭无非系统服务
turn_off()
{
    for i in `ls /etc/rc3.d/S*`
    do
        SRV=`echo $i|cut -c 15-`
    case $SRV in
        cloud-init|cloud-init-user-scripts|crond|irqbalance|local| \
        network|ntpd|ntpdate|sysstat|sshd|sendmail|yum-updatesd )
            echo "$SRV is a system service"
        ;;
        *)
            echo "Turn off $SRV"
            chkconfig --level 235 $SRV off
            service $SRV stop
        ;;
    esac
    done
}
shutdown_service()
{
    echo "Doing $FUNCNAME..."
    turn_off >> $LOG
    echo -e "Done $FUNCNAME\n"
}


# 关闭 Linux 防火墙
shutdown_firewall()
{
    echo "Doing $FUNCNAME..."
    cp -n /etc/rc.local $BACKUP_DIR/etc-rc.local
    cp -n /etc/selinux/config $BACKUP_DIR/etc-selinux-config
    # 关闭 iptables
    service iptables stop >> $LOG
    echo 'service iptables stop' >> /etc/rc.local

    # 关闭 selinux
    sed -ri 's/^SELINUX=.*/SELINUX=disabled/g' /etc/selinux/config

    # 关闭 setenforce
    setenforce 0  >> $LOG
    echo 'setenforce 0' >> /etc/rc.local
    echo -e "Done $FUNCNAME\n"
}


# 安装必要的 Linux 包
install_package()
{
    echo "Doing $FUNCNAME..."
    yum -y check-update  >> $LOG
    yum -y update  >> $LOG
    yum -y install gcc gcc-c++ make bzip2 sysstat net-snmp* ntp nfs-utils vim-common wget screen iptraf libxslt libxml2 keyutils-libs-devel libxml2-devel readline-devel bzip2-devel krb5-devel curl-devel libevent-devel libxslt-devel sqlite-devel db4-devel libgcrypt-devel e2fsprogs-devel ncurses-devel tcl-devel libselinux-devel libsepol-devel openssl-devel zlib-devel pcre-devel kernel-devel boost-devel libuuid-devel >> $LOG
    echo -e "Done $FUNCNAME\n"
}


# 修改 bashrc
set_bashrc()
{
echo "Doing $FUNCNAME..."

cat > /root/.bashrc <<EOF
# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

# User specific aliases and functions
export HISTTIMEFORMAT="%F %T > "

alias ls='ls --color=auto'
alias dir='dir --color=auto'
alias vdir='vdir --color=auto'

alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

alias l='ls -ClhF'
alias ll='ls -AlhF'
alias la='ls -A'

alias rmpyc='find ./ | grep pyc | xargs rm -f'
alias psgrep='ps auxf|grep -v grep|grep'
EOF
cat /root/.bashrc > /home/ec2-user/.bashrc

echo "
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'" >> /root/.bashrc

echo -e "Done $FUNCNAME\n"
}

# 修改 vimrc
set_vimrc()
{
echo "Doing $FUNCNAME..."
cat > /etc/vimrc <<EOF
if has("syntax")
  syntax on
endif

" Uncomment the following to have Vim jump to the last position when
" reopening a file
if has("autocmd")
  au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif
endif

" Uncomment the following to have Vim load indentation rules and plugins
" according to the detected filetype.
if has("autocmd")
  filetype plugin indent on
endif

" The following are commented out as they cause vim to behave a lot
" differently from regular Vi. They are highly recommended though.
set showcmd     " Show (partial) command in status line.
set showmatch       " Show matching brackets.
set ignorecase      " Do case insensitive matching
set smartcase       " Do smart case matching
set incsearch       " Incremental search

" Source a global configuration file if available
if filereadable("/etc/vim/vimrc.local")
  source /etc/vim/vimrc.local
endif
set nu
set autoindent
set cindent
set hlsearch

set nocompatible    "非兼容模式
set background=dark "背景色
color desert
set ruler           "在左下角显示当前文件所在行
set report=0        "显示修改次数
set nobackup        "无备份
set cursorline      "高亮当前行背景
set fileencodings=ucs-bom,UTF-8,GBK,BIG5,latin1
set fileencoding=UTF-8
set fileformat=unix "换行使用unix方式
set ambiwidth=double
set noerrorbells    "不显示响铃
set visualbell      "可视化铃声
set foldmarker={,}  "缩进符号
set foldmethod=indent   "缩进作为折叠标识
set foldlevel=100   "不自动折叠
set foldopen-=search    "搜索时不打开折叠
set foldopen-=undo  "撤销时不打开折叠
set updatecount=0   "不使用交换文件
set magic           "使用正则时，除了$ . * ^以外的元字符都要加反斜线

"缩进定义
set shiftwidth=4
set tabstop=4
set softtabstop=4
set expandtab
set smarttab
set backspace=2     "退格键可以删除任何东西

"映射常用操作
map [r :! python % <CR>
map [o :! python -i % <CR>
map [t :! rst2html.py % %<.html <CR>
EOF
echo -e "Done $FUNCNAME\n"
}


####################################################
###                  应用程序部署                  ###
####################################################


# 安装 App 服务器所需软件
# nginx mencache mongodb python py-package django uwsgi gearman ......
install_nginx()
{
    echo "Doing $FUNCNAME..."
    cd $DOWNLOAD_DIR
    wget -q $DOWNLOAD_SERVER/nginx-1.0.14.tar.gz
    tar xzf nginx-1.0.14.tar.gz
    cd nginx-1.0.14
    ./configure --prefix=/usr/local/nginx --with-http_ssl_module --with-http_stub_status_module --without-mail_pop3_module --without-mail_imap_module --without-mail_smtp_module --with-http_realip_module >> $LOG
    make -j 4 >> $LOG
    make install >> $LOG
    echo -e "Done $FUNCNAME\n"
}

install_python()
{
    echo "Doing $FUNCNAME..."
    cd $DOWNLOAD_DIR
    wget -q $DOWNLOAD_SERVER/Python-2.7.2.tgz
    tar xzf Python-2.7.2.tgz
    cd Python-2.7.2/
    ./configure >> $LOG
    make >> $LOG
    make install >> $LOG
    echo -e "Done $FUNCNAME\n"
}

install_pypackage()
{
    echo "Doing $FUNCNAME..."
    packages='
    setuptools-0.6c11.tar.gz Django-1.3.1.tar.gz pylibmc-1.2.2.tar.gz
    python-memcached-1.48.tar.gz xlrd-0.7.3.tar.gz gearman-2.0.2.tar.gz
    pymongo-2.1.1.tar.gz uwsgi-1.0.4.tar.gz
    '
    cd $DOWNLOAD_DIR
    for pkg in $packages;do
    echo install $pkg
    wget -q $DOWNLOAD_SERVER/pypi/$pkg
    tar xzf $pkg
    sleep 2
    cd ./${pkg%%.tar.gz}
    sleep 2
    /usr/local/bin/python ./setup.py install >> $LOG
    sleep 2
    cd ..
    done
    echo -e "Done $FUNCNAME\n"
}

install_gearman()
{
    echo "Doing $FUNCNAME..."
    cd $DOWNLOAD_DIR
    wget -q $DOWNLOAD_SERVER/gearmand-0.28.tar.gz
    tar -xzf gearmand-0.28.tar.gz
    cd gearmand-0.28
    ./configure >> $LOG
    make >> $LOG
    make install >> $LOG
    echo -e "Done $FUNCNAME\n"
}

install_memcached()
{
    echo "Doing $FUNCNAME..."
    cd $DOWNLOAD_DIR
    wget -q $DOWNLOAD_SERVER/memcached-1.4.10.tar.gz
    tar zxf memcached-1.4.10.tar.gz
    cd memcached-1.4.10/
    ./configure --prefix=/usr/local/memcached >> $LOG
    make >> $LOG
    make install >> $LOG
    echo -e "Done $FUNCNAME\n"
}

install_libmemcached()
{
    echo "Doing $FUNCNAME..."
    cd $DOWNLOAD_DIR
    wget -q $DOWNLOAD_SERVER/libmemcached-1.0.2.tar.gz
    tar zxf libmemcached-1.0.2.tar.gz
    cd libmemcached-1.0.2
    ./configure --with-memcached=/usr/local/memcached/bin/memcached >> $LOG
    make >> $LOG
    make install >> $LOG

    grep -q "/usr/local/lib" /etc/ld.so.conf || echo "/usr/local/lib" >> /etc/ld.so.conf
    ldconfig
    echo -e "Done $FUNCNAME\n"
}

install_mongodb()
{
    echo "Doing $FUNCNAME..."
    cd $DOWNLOAD_DIR
    wget -q $DOWNLOAD_SERVER/mongodb-linux-x86_64-2.0.2.tgz
    tar zxf mongodb-linux-x86_64-2.0.2.tgz
    cd mongodb-linux-x86_64-2.0.2
    mkdir -p /usr/local/mongodb
    cp -rf ./* /usr/local/mongodb/

    mkdir -p /data/db
    touch /data/log
    chmod -R 777 /data/db
    echo -e "Done $FUNCNAME\n"
}


# 创建环境 App 目录，修改为wheel组用户权限，生成启动脚本，日志文件
create_app_project()
{
echo "Doing $FUNCNAME..."
mkdir -p /opt/sites/city/logs
echo 'create app scripts...' >> $LOG
cd /opt/sites/city/
cat > start.sh << EOF
#!/bin/bash
# Constants
PDIR=/opt/sites/city
LDIR=/opt/sites/city/logs
PYTHON=/usr/local/bin/python
IMPORT_TEST=import_test
SETTINGS=settings
PORT=30000

# Import test
check() {
echo "Start import test ..."
(\$PYTHON \$PDIR/\$IMPORT_TEST.py )
}

# uWSGI start
start() {
echo ">> Start !"
/usr/local/bin/uwsgi -s 127.0.0.1:\$PORT \\
    --protocol uwsgi \\
    --master \\
    --processes 4 \\
    --cpu-affinity 1 \\
    --enable-threads \\
    --buffer-size 32768 \\
    --harakiri 30 \\
    --harakiri-verbose \\
    --listen 2000 \\
    --max-requests 32768 \\
    --pidfile \$LDIR/uwsgi.pid \\
    --daemonize \$LDIR/uwsgi.log \\
    --disable-logging \\
    --log-date \\
    --memory-report \\
    --log-micros \\
    --log-4xx \\
    --log-5xx \\
    --log-zero \\
    --log-big 1240 \\
    --env DJANGO_SETTINGS_MODULE=\$SETTINGS \\
    -w "django.core.handlers.wsgi:WSGIHandler()"
echo -e "City start done! \n"
}

# Main
cd \$PDIR
find ./ | grep '.pyc' | xargs rm -f
check
start
EOF

cat > stop.sh << EOF
#!/bin/bash
PORT=30000
LDIR=/opt/sites/city/logs

/usr/local/bin/uwsgi --stop \$LDIR/uwsgi.pid
ps auxf | grep -v grep | grep \$PORT | grep bin/uwsgi | kill -9 \`awk -F' ' '{print \$2}'\`

echo "Done !"
EOF

cat > restart.sh << EOF
#!/bin/bash
PDIR=/opt/sites/city

echo -e "\n"
\$PDIR/stop.sh
echo -e "\n"
\$PDIR/start.sh
EOF

chmod a+x start.sh stop.sh restart.sh

echo 'creat logs' >> $LOG
cd /opt/sites/city/logs/
touch uwsgi.log uwsgi.pid
chown -R ec2-user:wheel /opt/sites/
echo -e "Done $FUNCNAME\n"
}

set_nginx()
{
echo "Doing $FUNCNAME..."
echo 'set nginx conf...' >> $LOG
cat > /usr/local/nginx/conf/nginx.conf <<EOF
user  nobody;
worker_processes  4;
worker_cpu_affinity 0001 0010 0100 1000;
worker_rlimit_nofile 32768;

error_log  logs/error.log;

pid        logs/nginx.pid;

events {
    use epoll;
    worker_connections  32768;
}


http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;

    keepalive_timeout  60;
    server_names_hash_bucket_size 512;
    client_header_buffer_size 128k;
    large_client_header_buffers 4 128k;
    client_max_body_size 8m;

    gzip  on;

    log_format main '\$remote_addr [\$time_local] \$status \$request_time '
                    '\$request [\$body_bytes_sent/\$bytes_sent]   '
                    '\$http_user_agent';

    server {
        listen       80;
        server_name  46.137.223.56;
        merge_slashes off;
        location = /favicon.ico  {
            empty_gif;
            access_log off;
        }
        location /crossdomain.xml {
            expires 30d;
        }
        location ~^/\$|~*(php|html|htm)\$ {
            deny all;
            access_log off;
        }
        location /oc_nginx_check {
            stub_status on;
        }
        location /statics/ {
            root /opt/sites/city;
            expires 30d;
            access_log off;
        }
        location / {
            uwsgi_pass 127.0.0.1:30000;
            include uwsgi_params;
        }
        access_log  logs/access_city main;
        error_log   logs/error_city;
    }
}
EOF

echo 'create re-nginx script...' >> $LOG
cat > /usr/local/bin/re-nginx <<EOF
#!/bin/bash
echo -e "\t"
echo -e "Checking conf file ..."
/usr/local/nginx/sbin/nginx -t -c /usr/local/nginx/conf/nginx.conf
echo -e "\t"
echo -e "Restart ..."
/usr/local/nginx/sbin/nginx -s reload
echo -e "Done!"
echo -e "\n"
EOF
chmod a+x /usr/local/bin/re-nginx
echo -e "Done $FUNCNAME\n"
}

setup_app_env()
{
    echo "Doing $FUNCNAME..."
    install_nginx
    install_libmemcached
    install_python
    install_pypackage
    install_gearman
    create_app_project
    set_nginx
    echo -e "Done $FUNCNAME\n"
}


# 安装 Cache 服务器所需软件
create_cache_script()
{
echo "Doing $FUNCNAME..."
echo 'create start-cache script...' >> $LOG
cat > /usr/local/bin/start-cache <<EOF
#!/bin/bash
echo -e "\nKill memcached ..."
killall memcached
/usr/local/memcached/bin/memcached -d -p 19997 -t 8 -c 10240 -u nobody
echo -e "Memcached restart Done !"

echo -e "\t"
EOF
chmod a+x /usr/local/bin/start-cache
echo -e "Done $FUNCNAME\n"
}

setup_cache_env()
{
    echo "Doing $FUNCNAME..."
    install_memcached
    create_cache_script
    echo -e "Done $FUNCNAME\n"
}


# 安装 DB 服务器所需软件
create_db_script()
{
echo "Doing $FUNCNAME..."
echo 'create db script...' >> $LOG
cat > /usr/local/bin/start-db <<EOF
#!/bin/bash
/usr/local/bin/mongod \\
--port 21077 \\
--noauth \\
--maxConns 819 \\
--fork \\
--pidfilepath /data/mongo.pid \\
--logpath /data/mongo.log \\
--logappend \\
--dbpath /data/db \\
--cpu \\
--diaglog 1 \\
--directoryperdb \\
--journal \\
--journalCommitInterval 10 \\
--syncdelay 1800
EOF
chmod a+x /usr/local/bin/start-db
echo -e "Done $FUNCNAME\n"
}

setup_db_env()
{
    echo "Doing $FUNCNAME..."
    install_mongodb
    create_db_script
    echo -e "Done $FUNCNAME\n"
}


main()
{
    # 基础环境部分
    #set_ulimit            # 修改文件描述符
    #set_kernel            # 设置内核参数
    #shutdown_service      # 关闭无非系统服务
    #shutdown_firewall     # 关闭 Linux 防火墙
    #install_package       # 安装必要的 Linux 包
    #set_bashrc            # 修改 bashrc
    #set_vimrc             # 修改 vimrc

    # 应用环境部分
    # setup_app_env         # 部署应用服务器
    # setup_cache_env       # 部署缓存服务器
    # setup_db_env          # 部署数据库服务器
}

main
