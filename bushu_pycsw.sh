python3 -m venv --clear /home/bk/usr/vpy_csw/
. /home/bk/usr/vpy_csw/bin/activate

git clone https://gitee.com/gislite/pycsw.git
cd /home/bk/gitee/pycsw
/home/bk/usr/vpy_csw/bin/python3 -m pip install -e .
/home/bk/usr/vpy_csw/bin/python3 -m pip install -r requirements-standalone.txt