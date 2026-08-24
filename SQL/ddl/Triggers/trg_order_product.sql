CREATE TRIGGER trg_order_product
AFTER INSERT ON order_item
FOR EACH ROW
EXECUTE FUNCTION order_product();