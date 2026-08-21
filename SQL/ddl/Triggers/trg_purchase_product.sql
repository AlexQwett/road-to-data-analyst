CREATE TRIGGER trg_purchase_product
AFTER INSERT ON purchase_item
FOR EACH ROW
EXECUTE FUNCTION purchase_product();