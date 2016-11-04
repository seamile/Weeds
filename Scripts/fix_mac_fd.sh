# maxfiles >= maxfilesperproc >= ulimit

# 全局最大连接数 (系统默认: 12288)
sysctl -w kern.maxfiles=2097152

# 单个进程最大连接数 (系统默认: 10240)
sysctl -w kern.maxfilesperproc=1048576

# 当前 Shell 最大连接数 (系统默认: 256)
ulimit -n 1048576

# 动态端口号范围 (系统默认: 49152 ~ 65535)
sysctl -w net.inet.ip.portrange.first=8192
sysctl -w net.inet.ip.portrange.last=65535
