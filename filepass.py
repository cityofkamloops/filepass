import fs
import os
import fs.smbfs

# Load Environmental Variables
from_user = os.environ.get('FROMUSER')
from_pw = os.environ.get('FROMPW')
from_svr = os.environ.get('FROMSVR')
from_port = os.environ.get('FROMPORT')
from_dir = os.environ.get('FROMDIR')
from_share = os.environ.get('FROMSMBSHARE')
from_method = os.environ.get('FROMMETHOD')
from_delete = os.environ.get('FROMDELETE')
from_filter = os.environ.get('FROMFILEFILTER')

to_user = os.environ.get('TOUSER')
to_pw = os.environ.get('TOPW')
to_svr = os.environ.get('TOSVR')
to_port = os.environ.get('TOPORT')
to_dir = os.environ.get('TODIR')
to_share = os.environ.get('TOSMBSHARE')
to_method = os.environ.get('TOMETHOD')
to_delete = os.environ.get('TODELETE')

def logger(msg):
    print(msg)


# File Transfer Types
def ssh_connection(user, pw, svr, port, dir):
    logger('ssh://{}:{}@{}:{}{}'.format(user, pw, svr, port, dir))
    fs_conn = fs.open_fs('ssh://{}:{}@{}:{}{}'.format(user, pw, svr, port, dir))
    return fs_conn

def smb_connection(user, pw, svr, port, smbshare):
    svr = ("misc-fs-pv01","10.10.9.42")
    logger('smb://{}:{}@{}:{}/{}'.format(user, pw, svr, port, smbshare))

    fs_conn = fs.smbfs.SMBFS(
        svr, username='onorstrom@ad.kamloops.city', passwd=pw, timeout=15,
        port=445, name_port=139, direct_tcp=True, domain="CITYNDS"
    )

    # (ad.kamloops.city) (or look in the file I cent to marco CN=.......)

    #fs_conn = fs.open_fs('smb://{}:{}@{}:{}/{}'.format(user, pw, svr, port, smbshare))

    return fs_conn

def transfer_file(from_fs, to_fs, filename):
    to_fs.writefile(filename, from_fs.open(filename, 'rb'))


# From File System
if from_method == 'ssh':
    from_fs = ssh_connection(from_user, from_pw, from_svr, from_port, from_dir)
if from_method == 'smb':
    from_fs = smb_connection(from_user, from_pw, from_svr, from_port, from_share)

# To File System
if to_method == 'ssh':
    to_fs = ssh_connection(to_user, to_pw, to_svr, to_port, to_dir)
if to_method == 'smb':
    to_fs = smb_connection(to_user, to_pw, to_svr, to_port, to_share)


#walker = fs.walk.Walker(filter=[from_filter])
#for path in walker.files(from_fs):
#    print(path)
#    if to_delete == 'yes' and to_fs.exists(path):
#        to_fs.remove(path)
#    transfer_file(from_fs, to_fs, path)
#    if from_delete == 'yes' and from_fs.exists(path):
#        from_fs.remove(path)
