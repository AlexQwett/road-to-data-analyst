CREATE TRIGGER trg_update_product
BEFORE UPDATE ON product
FOR EACH ROW
EXECUTE FUNCTION set_update_product_time();