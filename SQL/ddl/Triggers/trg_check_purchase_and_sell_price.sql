CREATE TRIGGER trg_check_purchase_and_sell_price
BEFORE INSERT ON purchase_item
FOR EACH ROW
EXECUTE FUNCTION check_purchase_and_sell_price();