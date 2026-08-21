CREATE FUNCTION purchase_product()
RETURNS TRIGGER AS $$
DECLARE
	v_shop_id BIGINT;
BEGIN
    SELECT shop_id INTO v_shop_id FROM purchase WHERE purchase_id = NEW.purchase_id;

    INSERT INTO inventory (shop_id, product_id, quantity)
	VALUES (v_shop_id, NEW.product_id, NEW.quantity)
	ON CONFLICT (shop_id, product_id)
	DO UPDATE SET quantity = inventory.quantity + EXCLUDED.quantity;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;