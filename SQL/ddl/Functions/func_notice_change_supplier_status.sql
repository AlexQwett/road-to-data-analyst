CREATE FUNCTION notice_change_supplier_status()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.is_active = TRUE AND NEW.is_active = FALSE THEN
        RAISE NOTICE 'Статус постачальника % змінено на %', NEW.name, NEW.is_active;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;