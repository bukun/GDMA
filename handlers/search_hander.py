import tornado.web
import tornado.escape
from torcms.core.base_handler import BaseHandler
from owslib.csw import CatalogueServiceWeb
from owslib.fes import PropertyIsEqualTo, PropertyIsLike, BBox


class DirectorySearchHandler(BaseHandler):
    def initialize(self):
        super(DirectorySearchHandler, self).initialize()

    def get(self, url_str=''):
        url_arr = self.parse_url(url_str)
        if len(url_str) > 0:
            url_arr = url_str.split('/')
        if url_str == '':
            self.list('')
        elif url_arr[0] == 'search':
            self.search(url_arr[1], url_arr[2], url_arr[3], url_arr[4])
        elif url_arr[0] == 'view':
            self.ajax_get(url_arr[1], url_arr[2])

    def list(self, keyw):

        csw = CatalogueServiceWeb('https://ikcest-drr.osgeo.cn/csw')
        birds_query_like = PropertyIsLike('dc:title', '%{0}%'.format(keyw))
        csw.getrecords2(constraints=[birds_query_like], maxrecords=20)
        self.render('../torcms_dde/search/meta_index.html',
                    meta_results=csw.records,
                    userinfo=self.userinfo)

    def search(self, keyw, isweb, ldrt, max_num):
        '''
        :param keyw:
        :param isweb: 1 for local; 2 for federated
        :param ldrt: 空间范围的参数
        :param max_num:
        '''

        post_data = self.get_request_arguments()
        startnum = post_data.get('startnum', 0)
        startposition = int(startnum) * int(max_num) + 1

        # 原来部署
        # csw = CatalogueServiceWeb('https://ikcest-drr.osgeo.cn/csw')
        # 换为 OSGeo域名
        csw = CatalogueServiceWeb('https://ikcest-drr.osgeo.cn/csw')
        if ldrt:
            xx_ldrt = [float(x) for x in ldrt.split(',')]
            xx_ldrt = [xx_ldrt[1], xx_ldrt[0], xx_ldrt[3], xx_ldrt[2]]
            crs = 'EPSG:3857'
            bbox_query = BBox(xx_ldrt, crs)
            xinfo = {
                'start': startposition,
                'max': max_num,
                'bbox': xx_ldrt
            }
            print(xinfo)
            '''
            2023年： 使用空间范围检索是有问题的。此处暂时不实际使用空间范围检索功能。
            '''
            if isweb == '1':

                # csw.getrecords2(
                #     constraints=[bbox_query],
                #     startposition=startposition,
                #     maxrecords=int(max_num)
                # )
                kw_query = PropertyIsLike('csw:AnyText', '%{0}%'.format('earthquake'))
                csw.getrecords2(constraints=[kw_query],
                                maxrecords=6,
                                startposition=startposition,
                                distributedsearch=True,
                                hopcount=2)

            else:
                kw_query = PropertyIsLike('csw:AnyText', '%{0}%'.format(keyw))
                # csw.getrecords2(constraints=[kw_query, bbox_query],
                csw.getrecords2(constraints=[kw_query],
                                maxrecords=max_num,
                                startposition=startposition,
                                distributedsearch=True,
                                hopcount=2)
        else:
            if isweb == '1':

                kw_query = PropertyIsLike('dc:title', '%{0}%'.format(keyw))

                csw.getrecords2(constraints=[kw_query],
                                startposition=startposition,
                                maxrecords=max_num)
            else:
                kw_query = PropertyIsLike('csw:AnyText', '%{0}%'.format(keyw))
                csw.getrecords2(constraints=[kw_query],
                                maxrecords=max_num,
                                startposition=startposition,
                                distributedsearch=True,
                                hopcount=2)
        for rec in csw.records:
            print(rec)
        self.render('../torcms_dde/search/show_result.html',
                    meta_results=csw.records,
                    userinfo=self.userinfo,
                    isweb=isweb,
                    startnum=startnum,
                    keyword=keyw
                    )

    def ajax_get(self, uuid, isweb):
        csw = CatalogueServiceWeb('https://ikcest-drr.osgeo.cn/csw')

        csw.getrecordbyid(id=[uuid])
        if isweb == '1':
            rec = csw.records.get(uuid)
        else:
            birds_query = PropertyIsLike('csw:AnyText', uuid)
            csw.getrecords2(constraints=[birds_query], maxrecords=20, startposition=0, distributedsearch=True,
                            hopcount=2)
            print(csw.results)
            for key in csw.records:
                rec = csw.records[key]

        out_dict = {
            'title': '',
            'uid': '',
            'sizhi': '',

        }

        self.render('../torcms_dde/search/show_rec.html',
                    kws=out_dict,
                    # meta_rec=csw.records.get(uuid),
                    meta_rec=rec,
                    unescape=tornado.escape.xhtml_unescape,
                    userinfo=self.userinfo
                    )


class MyXML():
    def __init__(self, in_ele):
        self.element = in_ele

    def uid(self):
        for sub_ele in self.element.iter():
            if 'identifier' == sub_ele.tag.split('}')[1]:
                return sub_ele.text

    def recordPosition(self):
        for sub_ele in self.element.iter():
            if 'recordPosition' == sub_ele.tag.split('}')[1]:
                return sub_ele.text

    def sizhi(self):
        out_arr = [0, 0, 0, 0]
        for sub_ele in self.element.iter():
            if 'LowerCorner' == sub_ele.tag.split('}')[1]:
                t1 = sub_ele.text.split(' ')
                out_arr[0] = float(t1[0])
                out_arr[2] = float(t1[1])
            if 'UpperCorner' == sub_ele.tag.split('}')[1]:
                t2 = sub_ele.text.split(' ')
                out_arr[1] = float(t2[0])
                out_arr[3] = float(t2[1])
        return out_arr

    def title(self):
        for sub_ele in self.element.iter():
            if 'title' == sub_ele.tag.split('}')[1]:
                return sub_ele.text
