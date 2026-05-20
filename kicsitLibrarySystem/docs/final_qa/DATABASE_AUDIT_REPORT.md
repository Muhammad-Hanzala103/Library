# Database Audit Report

Static metadata result: all 32 required table names exist in SQLAlchemy metadata.

Live database result: Fail/Blocked because MySQL refused `127.0.0.1:3306`.

## Consistency SQL Checks To Run After MySQL Starts

```sql
SELECT accession_number, COUNT(*) FROM bookcopies GROUP BY accession_number HAVING COUNT(*) > 1;
SELECT bc.id FROM bookcopies bc JOIN issuerecords ir ON ir.book_copy_id = bc.id AND ir.status='Active' WHERE bc.status='Available';
SELECT bc.id FROM bookcopies bc LEFT JOIN issuerecords ir ON ir.book_copy_id = bc.id AND ir.status='Active' WHERE bc.status='Issued' AND ir.id IS NULL;
SELECT ir.id FROM issuerecords ir LEFT JOIN bookcopies bc ON bc.id = ir.book_copy_id WHERE ir.status='Active' AND bc.id IS NULL;
SELECT ir.id FROM issuerecords ir WHERE ir.status='Active' AND ir.student_id IS NULL AND ir.employee_id IS NULL;
SELECT rr.id FROM receiverecords rr LEFT JOIN issuerecords ir ON ir.id = rr.issue_record_id WHERE ir.id IS NULL;
SELECT f.id FROM fines f LEFT JOIN issuerecords ir ON ir.id = f.issue_record_id WHERE f.issue_record_id IS NOT NULL AND ir.id IS NULL;
SELECT r.id FROM reservations r WHERE r.status='Ready for pickup' AND r.book_copy_id IS NULL;
SELECT bm.id FROM bookmasters bm JOIN bookcopies bc ON bc.book_master_id=bm.id JOIN issuerecords ir ON ir.book_copy_id=bc.id AND ir.status='Active' WHERE bm.is_deleted=1;
SELECT s.id FROM students s JOIN issuerecords ir ON ir.student_id=s.id AND ir.status='Active' WHERE s.clearance_status='Cleared';
SELECT s.id FROM students s JOIN fines f ON f.student_id=s.id AND f.payment_status IN ('Unpaid','Partial') WHERE s.clearance_status='Cleared';
SELECT lb.id FROM lostbooks lb JOIN bookcopies bc ON bc.id=lb.book_copy_id WHERE bc.status='Available';
SELECT db.id FROM damagedbooks db JOIN bookcopies bc ON bc.id=db.book_copy_id WHERE bc.status='Available';
```

## Metadata Gaps

- Some lookup tables lack `created_at`/`updated_at`.
- Some unique constraints are expressed through column flags and are not counted as explicit `UniqueConstraint` objects.
- Database-level check constraints for status values and non-negative numeric values are limited.

