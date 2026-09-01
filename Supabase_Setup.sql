-- ====================================================================
-- SUPABASE DATABASE SETUP FOR GROWTH TRACKER
-- Run this script in your Supabase SQL Editor (Database -> SQL Editor)
-- ====================================================================

-- 1. Create growth_months table
CREATE TABLE IF NOT EXISTS public.growth_months (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE DEFAULT auth.uid(),
  month_key TEXT NOT NULL,
  tracker_data JSONB DEFAULT '{}'::jsonb,
  intentions JSONB DEFAULT '{}'::jsonb,
  books JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT unique_user_month UNIQUE (user_id, month_key)
);

-- 2. Enable Row Level Security (RLS)
ALTER TABLE public.growth_months ENABLE ROW LEVEL SECURITY;

-- 3. Drop existing policies if re-running
DROP POLICY IF EXISTS "Users can select their own growth months" ON public.growth_months;
DROP POLICY IF EXISTS "Users can insert their own growth months" ON public.growth_months;
DROP POLICY IF EXISTS "Users can update their own growth months" ON public.growth_months;
DROP POLICY IF EXISTS "Users can delete their own growth months" ON public.growth_months;

-- 4. Create RLS Policies for authenticated users
CREATE POLICY "Users can select their own growth months"
  ON public.growth_months FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own growth months"
  ON public.growth_months FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own growth months"
  ON public.growth_months FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own growth months"
  ON public.growth_months FOR DELETE
  USING (auth.uid() = user_id);

-- 5. Create automatic updated_at trigger function
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_growth_months_modtime ON public.growth_months;
CREATE TRIGGER update_growth_months_modtime
    BEFORE UPDATE ON public.growth_months
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- Optional: Add real-time sync table publication
ALTER PUBLICATION supabase_realtime ADD TABLE public.growth_months;
