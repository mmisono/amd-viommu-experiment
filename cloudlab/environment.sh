if [ -z ${NAME+x} ]; then
    echo "Please set \$NAME";
    exit
fi

if [ -z ${USER+x} ]; then
    echo "Please set \$USER";
    exit
fi

export PORT=22
export SERVER=${USER}@${NAME}.utah.cloudlab.us
export SCRIPTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
export SSHKEY=${SSHKEY:-${SCRIPTDIR}/id_rsa}

$SHELL
