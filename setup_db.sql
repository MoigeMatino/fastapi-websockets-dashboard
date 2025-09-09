-- Create the inventory table
CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create the trigger function for notifications
CREATE OR REPLACE FUNCTION notify_inventory_changes() RETURNS trigger AS $$
DECLARE
  payload JSON;
BEGIN
  IF (TG_OP = 'DELETE') THEN
    payload = json_build_object('event', TG_OP, 'data', row_to_json(OLD));
  ELSE -- if operation is INSERT or UPDATE--
    payload = json_build_object('event', TG_OP, 'data', row_to_json(NEW));
  END IF;
  PERFORM pg_notify('inventory_channel', payload::text);
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Create the trigger
DROP TRIGGER IF EXISTS inventory_trigger ON inventory;
CREATE TRIGGER inventory_trigger
AFTER INSERT OR UPDATE OR DELETE ON inventory
FOR EACH ROW EXECUTE FUNCTION notify_inventory_changes();