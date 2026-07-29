-- Dynamic (mechanistic) models seed. `information` holds the detailed metadata
-- the UI renders. Idempotent (skips if a model with the same name exists).
BEGIN;

INSERT INTO public.dynamic_model (id, name, version, url_endpoint, information)
SELECT gen_random_uuid(), v.name, v.version, v.url_endpoint, v.info::json
FROM (VALUES
(
 'IndPenSim penicillin', '2.0', NULL,
 '{"type":"unstructured kinetic","process":"Penicillin fed-batch fermentation","status":"calibrated",
   "state_variables":[
     {"symbol":"X","name":"Biomass concentration","units":"g/L","initial":"0.1","description":"Viable P. chrysogenum biomass"},
     {"symbol":"S","name":"Substrate (glucose)","units":"g/L","initial":"15.0","description":"Growth-limiting carbon source"},
     {"symbol":"P","name":"Penicillin titer","units":"g/L","initial":"0.0","description":"Product concentration"},
     {"symbol":"DO","name":"Dissolved oxygen","units":"mg/L","initial":"8.0","description":"Aeration / O2 limitation state"},
     {"symbol":"V","name":"Broth volume","units":"L","initial":"58000","description":"Working volume (fed-batch)"},
     {"symbol":"CO2","name":"Off-gas CO2","units":"%","initial":"0.04","description":"Metabolic activity indicator"}],
   "parameters":[
     {"name":"mu_max","value":"0.11","units":"1/h","source":"fitted","description":"Maximum specific growth rate"},
     {"name":"K_s","value":"0.15","units":"g/L","source":"literature","description":"Monod half-saturation (substrate)"},
     {"name":"K_DO","value":"0.50","units":"mg/L","source":"literature","description":"O2 half-saturation constant"},
     {"name":"Y_xs","value":"0.47","units":"g/g","source":"fitted","description":"Biomass yield on substrate"},
     {"name":"Y_ps","value":"1.20","units":"g/g","source":"fitted","description":"Penicillin yield on substrate"},
     {"name":"m_s","value":"0.014","units":"g/g/h","source":"literature","description":"Maintenance coefficient"},
     {"name":"q_p_max","value":"0.0055","units":"g/g/h","source":"fitted","description":"Max specific penicillin production"},
     {"name":"K_p","value":"2e-4","units":"g/L","source":"fitted","description":"Product-inhibition constant"},
     {"name":"k_h","value":"0.010","units":"1/h","source":"literature","description":"Penicillin hydrolysis rate"},
     {"name":"k_La","value":"120","units":"1/h","source":"fitted","description":"Oxygen transfer coefficient"},
     {"name":"k_d","value":"0.008","units":"1/h","source":"fitted","description":"Biomass death/lysis rate"}],
   "equations":"dX/dt = (mu - k_d)*X\ndS/dt = -(1/Y_xs)*mu*X - m_s*X + F*S_f/V\ndP/dt = q_p*X - k_h*P\ndV/dt = F\nmu   = mu_max * S/(K_s+S) * DO/(K_DO+DO)\nq_p  = q_p_max * S/(K_s+S) * K_p/(K_p+P)",
   "assumptions":["Well-mixed single-compartment bioreactor","Temperature and pH held at setpoint by control loops","Single growth-limiting substrate (glucose)","No explicit lag phase; morphology not resolved","Oxygen transfer via constant k_La; no CO2 inhibition"],
   "references":"Goldrick et al. 2015 - doi:10.1016/j.jbiotec.2014.10.029",
   "run_conditions":{"initial_conditions":"X=0.1, S=15, P=0 g/L; V=58 kL","feed_profile":"exponential (0-60 h) then constant","duration":"230 h","solver":"CVODE (BDF), rtol 1e-6"},
   "calibration":[{"state":"Biomass X","rmse":"1.8 g/L","r2":"0.97","vs":"batches 1-40"},{"state":"Substrate S","rmse":"0.6 g/L","r2":"0.94","vs":"batches 1-40"},{"state":"Penicillin P","rmse":"0.09 g/L","r2":"0.96","vs":"batches 1-40"}]}'
),
(
 'E. coli fed-batch', '1.1', 'http://r-api:8501/dynamic/ecoli',
 '{"type":"structured","process":"Recombinant protein production","status":"calibrated",
   "state_variables":[
     {"symbol":"X","name":"Biomass","units":"g/L","initial":"0.5","description":"E. coli dry cell weight"},
     {"symbol":"S","name":"Glucose","units":"g/L","initial":"20.0","description":"Carbon source"},
     {"symbol":"A","name":"Acetate","units":"g/L","initial":"0.0","description":"Overflow metabolite"},
     {"symbol":"P","name":"Product","units":"g/L","initial":"0.0","description":"Recombinant protein"},
     {"symbol":"DO","name":"Dissolved oxygen","units":"%","initial":"100","description":"Aeration state"},
     {"symbol":"V","name":"Volume","units":"L","initial":"5.0","description":"Broth volume"}],
   "parameters":[
     {"name":"mu_max","value":"0.55","units":"1/h","source":"fitted","description":"Max specific growth rate"},
     {"name":"K_s","value":"0.05","units":"g/L","source":"literature","description":"Glucose affinity"},
     {"name":"Y_xs","value":"0.42","units":"g/g","source":"fitted","description":"Biomass yield"},
     {"name":"q_ac","value":"0.15","units":"g/g/h","source":"fitted","description":"Acetate overflow rate"}],
   "equations":"dX/dt = mu*X\ndS/dt = -q_s*X + F*S_f/V\ndA/dt = q_ac*X - q_a_upt*X\ndP/dt = q_p*X\ndV/dt = F",
   "assumptions":["Overflow metabolism above critical growth rate","IPTG induction modelled as a step in q_p","Well-mixed reactor"],
   "references":"internal calibration, TBI pilot plant",
   "run_conditions":{"initial_conditions":"X=0.5, S=20 g/L; V=5 L","feed_profile":"exponential feed post batch phase","duration":"30 h","solver":"LSODA"},
   "calibration":[{"state":"Biomass X","rmse":"0.9 g/L","r2":"0.95","vs":"3 cultivations"}]}'
),
(
 'Monod biomass', '1.0', NULL,
 '{"type":"unstructured","process":"Generic microbial growth","status":"draft",
   "state_variables":[
     {"symbol":"X","name":"Biomass","units":"g/L","initial":"0.1","description":"Cell concentration"},
     {"symbol":"S","name":"Substrate","units":"g/L","initial":"10.0","description":"Limiting nutrient"}],
   "parameters":[
     {"name":"mu_max","value":"0.4","units":"1/h","source":"literature","description":"Max specific growth rate"},
     {"name":"K_s","value":"0.5","units":"g/L","source":"literature","description":"Half-saturation constant"},
     {"name":"Y_xs","value":"0.5","units":"g/g","source":"literature","description":"Yield coefficient"}],
   "equations":"dX/dt = mu*X\ndS/dt = -(1/Y_xs)*mu*X\nmu   = mu_max * S/(K_s+S)",
   "assumptions":["Batch culture","Single limiting substrate","No death or maintenance"],
   "references":"Monod 1949",
   "run_conditions":{"initial_conditions":"X=0.1, S=10 g/L","feed_profile":"batch (no feed)","duration":"24 h","solver":"RK45"},
   "calibration":[]}'
)
) AS v(name, version, url_endpoint, info)
WHERE NOT EXISTS (SELECT 1 FROM public.dynamic_model d WHERE d.name = v.name);

COMMIT;
