CREATE FUNCTION check_purchase_and_sell_price()
RETURNS TRIGGER AS $$
DECLARE
    p_sell_price NUMERIC(10,2);
BEGIN
    SELECT sell_price INTO p_sell_price FROM product WHERE product_id = NEW.product_id;
    
    IF p_sell_price <= NEW.purchase_price THEN
        RAISE EXCEPTION 'Закупівельна ціна більша або дорівнює продажній.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;