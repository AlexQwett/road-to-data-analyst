CREATE FUNCTION order_product()
RETURNS TRIGGER AS $$
DECLARE
	v_shop_id BIGINT;
	o_current_quantity INT;
BEGIN
	SELECT shop_id INTO v_shop_id FROM orders WHERE order_id = NEW.order_id;
	
	SELECT quantity INTO o_current_quantity
	FROM inventory
	WHERE shop_id = v_shop_id AND product_id = NEW.product_id;

	IF NOT FOUND THEN
		RAISE EXCEPTION 'Товару немає в inventory для цього магазину';
	END IF;

	IF o_current_quantity < NEW.quantity THEN
		RAISE EXCEPTION 'Товару не вистачає в inventory для цього магазину';
	END IF;

	UPDATE inventory SET quantity = quantity - NEW.quantity WHERE (shop_id, product_id) = (v_shop_id, NEW.product_id);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;