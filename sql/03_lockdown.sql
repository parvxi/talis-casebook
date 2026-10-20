-- Close the Supabase Data API path to the quiz tables (run AFTER 02_roles.sql)
-- Supabase auto-grants anon/authenticated full access to tables in public, which the
-- public REST API uses. The app never needs that path: students reach the data only
-- through quiz_runner over the Session pooler.
-- Re-run this file whenever 01_schema_seed.sql is re-run (it recreates the tables).

REVOKE ALL ON public.staff, public.beans, public.shipments, public.orders, public.badge_logs
  FROM anon, authenticated;

-- Second layer: Row Level Security. With RLS on and no policy, anon/authenticated see nothing.
-- quiz_runner gets an explicit read-only policy.
DO $$
DECLARE t TEXT;
BEGIN
  FOREACH t IN ARRAY ARRAY['staff','beans','shipments','orders','badge_logs'] LOOP
    EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', t);
    EXECUTE format('DROP POLICY IF EXISTS quiz_runner_read ON public.%I', t);
    EXECUTE format('CREATE POLICY quiz_runner_read ON public.%I FOR SELECT TO quiz_runner USING (true)', t);
  END LOOP;
END
$$;
