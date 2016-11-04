#!/bin/bash
#
#   代码发布脚本
#
#   Auth: Seamile   Version: 0.1
#   Date: 2012-11-02
#
#   使用说明：
#       执行 ./release [env] [tag_id]
#       Args:
#           env    -> 要发布到的环境  测试环境tes  生产环境prd
#           tag_id -> tag 号


if [ $# -ne 2 ]; then
    echo "请输入正确的参数！"
    exit 1
else
    case $1 in
        "test"|"prd")
        ENV=$1
        ;;
        *)
        echo "请输入正确的 env ！"
        exit 1
        ;;
    esac

    TAG=$2
    if [ ! -n "$TAG" ];then
        echo "请输入 tag ！"
        exit 1
    fi
fi


# 初始化变量
GIT_SVR="git@github.com:test.git"
TES_IP="x.x.x.x"
PRD_IP="x.x.x.x"
SERVER_DIR="$SRV:/opt/xxx"
SRC_DIR=/usr/local/src/xxx

if [ $ENV == "prd" ];then
    SRV="root@$PRD_IP"
else
    SRV="root@$TES_IP"
fi


# 创建源码文件夹,并克隆源码
cd $HOME
rm -rf $SRC_DIR
git clone $GIT_SVR $SRC_DIR

# 切换代码到对应 TAG
cd $SRC_DIR
git checkout $TAG


# 同步测试
echo "代码发布测试。以下代码将被发布到 $ENV 服务器 $SERVER_DIR"
cd $SRC_DIR
rsync -ncrvP --delete --exclude=.git* --exclude=*.c --exclude=demo --exclude=Makefile ./ $SERVER_DIR

# 同步
read -p "
确定发布代码到 $SERVER_DIR 吗?
(输入 y 确定, n 退出) >>> " input
if [ "x$input" == "xy" ]; then
    cd $SRC_DIR
    rsync -crvP --delete --exclude=.git* --exclude=*.c --exclude=demo --exclude=Makefile ./ $SERVER_DIR
else
    echo "退出同步"
    exit 0
fi
