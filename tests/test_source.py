import base64
import json
import unittest
from book_benefit_data.capture import normalize, source_config
from book_benefit_data.cli import resource, validate


class SourceTests(unittest.TestCase):
    def raw(self):
        source=resource('source.json')
        if source['access']=='html': return b'<h1>Chevening in Thailand</h1><p>Open for applications until 6 October 2026, at 11:00 (UTC)</p>'
        if source['access']=='github-api': return json.dumps({'encoding':'base64','name':'about-github-education-for-students.md','content':base64.b64encode(b'title: About GitHub Education for students').decode()}).encode()
        return json.dumps({'base_path':source['source_url'].removeprefix('https://www.gov.uk'),'title':'Universal Credit' if source['domain']=='benefit' else 'Apply for innovation funding','details':{}}).encode()

    def test_parse_and_validate_v2(self):
        source=resource('source.json')
        data=normalize(self.raw(),source,'2026-09-07T00:00:00Z')
        for item in data['items']: item['provenance'].update(raw_object_key='landing/test',bronze_manifest_key='control/manifests/test')
        self.assertEqual(validate(data)['schema_version'],source['schema_version'])
        self.assertTrue(any(v is None for v in data['items'][0]['terms'].values()))

    def test_unknown_terms_not_false(self):
        data=normalize(self.raw(),resource('source.json'),'2026-09-07T00:00:00Z')
        self.assertNotIn(False,data['items'][0]['terms'].values())

    def test_source_drift_rejected(self):
        with self.assertRaises((ValueError,KeyError)):
            normalize(b'{}',resource('source.json'),'2026-09-07T00:00:00Z')

    def test_missing_lineage_rejected(self):
        data=normalize(self.raw(),resource('source.json'),'2026-09-07T00:00:00Z')
        with self.assertRaises(ValueError): validate(data)

    def test_v1_still_supported(self):
        self.assertEqual(validate(resource('demo.json'))['data_status'],'fixture')

    def test_exact_deadline_or_unknown(self):
        source=resource('source.json')
        item=normalize(self.raw(),source,'2026-09-07T00:00:00Z')['items'][0]
        if source['domain']=='scholarship':
            self.assertEqual(item['deadline']['at'],'2026-10-06T11:00:00Z')
            self.assertEqual(item['status'],'open')
            later=normalize(self.raw(),source,'2026-10-06T11:00:00Z')['items'][0]
            self.assertEqual(later['status'],'closed')
        else:
            self.assertEqual(item['deadline']['kind'],'unknown')
            self.assertEqual(item['status'],'unknown')

    def test_thai_welfare_intake_variants(self):
        source=source_config('thaigov-state-welfare-2569')
        raw=('รัฐบาลไทย โครงการสวัสดิการแห่งรัฐ ปี 2569 '
             'ผู้มีสิทธิรายเดิมเริ่มใช้สิทธิฯ ได้ตั้งแต่วันที่ 1 สิงหาคม 2569 '
             'ผู้มีสิทธิรายใหม่เริ่มใช้สิทธิฯ ได้ตั้งแต่วันที่ 1 ตุลาคม 2569').encode()
        data=normalize(raw,source,'2026-09-07T00:00:00Z')
        for item in data['items']:
            item['provenance'].update(raw_object_key='landing/test',bronze_manifest_key='control/manifests/test')
        self.assertEqual(validate(data)['schema_version'],'benefit.v2')
        self.assertEqual(len(data['items']),2)
        self.assertEqual(data['items'][0]['availability']['starts_at'],'2026-08-01T00:00:00Z')
        self.assertEqual(data['items'][1]['availability']['kind'],'scheduled')
        self.assertEqual(data['items'][1]['availability']['starts_at'],'2026-10-01T00:00:00Z')

    def test_thai_water_support_is_utility_credit(self):
        source=source_config('thaigov-water-support-2569')
        raw=('รัฐบาลไทย เปิดลงทะเบียนสิทธิลดค่าน้ำประปา สำหรับผู้ผ่านบัตรสวัสดิการแห่งรัฐ '
             'เริ่ม 20 กรกฎาคม 2569 สนับสนุนไม่เกิน 100 บาทต่อครัวเรือนต่อเดือน '
             'กรณีค่าน้ำไม่เกิน 315 บาท').encode()
        data=normalize(raw,source,'2026-09-07T00:00:00Z')
        for item in data['items']:
            item['provenance'].update(raw_object_key='landing/test',bronze_manifest_key='control/manifests/test')
        self.assertEqual(validate(data)['schema_version'],'benefit.v2')
        self.assertEqual(len(data['items']),1)
        self.assertEqual(data['items'][0]['category'],'utility-support')
        self.assertEqual(data['items'][0]['value'],{'kind':'credit','amount':100,'currency':'THB','guaranteed':False})
        self.assertEqual(data['items'][0]['availability']['kind'],'continuous')

if __name__=='__main__': unittest.main()
