CREATE TRIGGER trg_notice_change_supplier_status
AFTER UPDATE ON supplier
FOR EACH ROW
EXECUTE FUNCTION notice_change_supplier_status();