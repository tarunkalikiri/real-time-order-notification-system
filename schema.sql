CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255),
    product_name VARCHAR(255),
    status VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION notify_order_change()
RETURNS TRIGGER AS $$
DECLARE
    payload JSON;
BEGIN
    IF TG_OP = 'DELETE' THEN
        payload = json_build_object(
            'operation', TG_OP,
            'id', OLD.id
        );
    ELSE
        payload = json_build_object(
            'operation', TG_OP,
            'id', NEW.id,
            'customer_name', NEW.customer_name,
            'product_name', NEW.product_name,
            'status', NEW.status
        );
    END IF;

    PERFORM pg_notify('orders_channel', payload::text);

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER orders_trigger
AFTER INSERT OR UPDATE OR DELETE
ON orders
FOR EACH ROW
EXECUTE FUNCTION notify_order_change();