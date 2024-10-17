
import requests
pre = 'https://ikcest-drr.osgeo.cn/csw'

def test_a(url):
    # url = pre + '?service=CSW&version=3.0.0&request=GetCapabilities'
    print(url)
    vv = requests.get(url)
    print(vv)
    assert vv.status_code == 200


if __name__ == '__main__':
    idx = 1
    for cnt in open('./info.list').readlines():
        line = cnt.strip()
        if line:
            print('=' * 40)
            print(idx)
            print(line)
            test_a(line)
        idx = idx + 1