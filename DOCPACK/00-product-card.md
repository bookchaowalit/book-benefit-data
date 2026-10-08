---
title: Book Benefit Data — Product Card
doc_id: CARD-book-benefit-data
doc_type: product-card
verdict: merge
version: 0.1
date: 2026-10-08
status: ร่างเพื่อพิจารณา
owner: Product owner (Book Dev)
---

# Book Benefit Data — Product Card

## 1. สรุปคุณค่าในหนึ่งประโยค

ช่วยคนทำงานอิสระและทีมเล็กค้นหาสิทธิประโยชน์และความช่วยเหลือ จากแหล่งทางการ โดยแยกค่าที่ไม่รู้ออกจากค่าที่เป็นเท็จ — แต่คุณค่าจริงอยู่ที่ schema และรายการแหล่งของโดเมนนี้ ไม่ใช่ที่ตัว repo แยก

## 2. ปัญหาและผู้ใช้เป้าหมาย

- ปัญหา: ข้อมูลสิทธิประโยชน์และความช่วยเหลือ กระจายอยู่หลายเว็บทางการ เงื่อนไข (คุณสมบัติ เส้นตาย มูลค่า) อ่านยากและเปลี่ยนบ่อย
- ผู้ใช้เป้าหมายตาม README: people and small teams; ผู้ใช้จริงตอนนี้คือ operator คนเดียว **[ต้องยืนยัน]** ว่ามีผู้ใช้อื่น

## 3. สิ่งที่ทำได้จริงตอนนี้

- CLI `book-benefit-data`: `contract`, `demo` (ค้นหา synthetic examples พร้อมตัวกรอง `--open-only`), `validate` export ตาม `benefit.v1 (+ schema-v2)`
- `capture.py`: เก็บแบบ manual จากแหล่งทางการ 6 ไฟล์ `source-*.json` (GOV.UK (court fee remission, DSA, housing benefit), NHS travel, thaigov state welfare 2569, thaigov water support 2569) ผ่าน shared lake runtime ของ parent — ไม่ fallback ไป fixture
- subcategories: public-assistance, utility-support, housing-support, member-benefit, accessibility, fee-waiver
- ไม่มี scheduler ใน repo, ไม่มี hosted API, ไม่มี consumer integration (README ระบุเอง)

## 4. หลักฐานสถานะ

| รายการ | ค่า (ตรวจจาก repository) |
|---|---|
| Stack | Python |
| Commits | 10 (แรก 2026-09-09 → ล่าสุด 2026-10-01) |
| Source | 9 ไฟล์ / 948 บรรทัด |
| Tests | 5 ไฟล์ |
| CI | 1 workflow |
| Deploy config | ไม่มี |
| Live URL | ไม่มี |
| README | 149 บรรทัด (`book-benefit-data`) |
| โครงสร้างซ้ำ (template family) | 13 repo ที่มี structure signature เดียวกัน |

`cli.py` ของ repo ในกลุ่มนี้ต่างจาก `book-grant-data` เพียงราว 14–66 บรรทัด (หลังแทนชื่อโดเมน) — โค้ดเกือบทั้งหมดซ้ำกัน

## 5. คุณค่าและจุดต่าง

- จุดต่าง: แยก value kind (cash/credit/discount/in-kind) ไม่รวมเป็นรายได้, label `live` ต้องมี lineage, ไม่เดาค่าที่ไม่รู้ — เป็นวินัยข้อมูลที่ดี
- มุมรายได้/การใช้ซ้ำ: เป็น feed ให้ "opportunity finder" รวมหลายโดเมนสำหรับ freelancer/SME ไทย **[สมมติฐาน]** — ยังไม่มีหลักฐานว่ามีคนจ่าย

## 6. ช่องว่างสำคัญ

- โดเมนเดียวมี 4–6 แหล่ง ไม่พอเป็นผลิตภัณฑ์เดี่ยว; ไม่มี UI/API ให้ผู้ใช้ปลายทาง
- 14 repo ใน discovery portfolio ใช้ CLI/capture ซ้ำกัน ทำให้แก้ bug หนึ่งครั้งต้องแก้ 14 ที่
- ยังไม่มี schedule ที่สังเกตได้, ไม่มี freshness SLO ที่ monitor อ่าน (ดู goal ใน roadmap)

## 7. คำตัดสิน

**`merge`** — โดเมนนี้มีคุณค่าในฐานะ schema + source registry แต่ไม่ควรเป็น repo/ผลิตภัณฑ์แยก ให้รวมเข้า canonical `book-grant-data` (ในฐานะฐานของผลิตภัณฑ์ discovery รวม) เป็น domain plugin (schema + `source-*.json`) ข้อเสนอนี้ขัดกับการแยก repo ตามโดเมนใน `discovery-portfolio.md` จึงต้องให้เจ้าของตัดสิน **[ต้องยืนยัน]**; จะเปลี่ยนเป็น `invest` แยกได้เมื่อมีผู้ใช้/ผู้ซื้อเฉพาะโดเมนนี้จริงและมี consumer ที่อ่าน feed

## 8. ขั้นต่อไป

1. เจ้าของตัดสินว่าจะรวม discovery 14 โดเมนเป็น repo เดียว (domain plugin) หรือคงแยก
2. ถ้ารวม: ย้าย schema + `source-*.json` เข้า canonical แล้ว archive repo นี้หลังอนุมัติ
3. ถ้าคงแยก: ดึง `cli.py`/`capture.py` ที่ซ้ำไปเป็น shared package เดียว

## การอนุมัติ

| บทบาท | สถานะ | วันที่ | ลงนาม |
|---|---|---|---|
| Product owner (Book Dev) | รอพิจารณา | — | ________ |

## แหล่งข้อมูล

- `README.md`
- `PRODUCT.md`
- `sources.json`
- `src/book_benefit_data/cli.py`
- `src/book_benefit_data/capture.py`
- `(solo-empire) systems/architecture/discovery-portfolio.md`
- `(solo-empire) repository-catalog/roadmaps/data-scrapers.yaml`
