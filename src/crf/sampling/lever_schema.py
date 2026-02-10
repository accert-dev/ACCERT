LEVER_ORDER = [
  "num_orders",
  "itc_percent",
  "n_itc",
  "interest_percent",
  "design_completion_percent",
  "design_maturity",
  "proc_exp",
  "N_proc",
  "ce_exp",
  "N_cons",
  "ae_exp",
  "N_AE",
  "standardization_percent",
  "modularity_code",
  "bop_grade_code",
  "rb_grade_code",
]

STATIC_KEYS = [
  "Num_orders", "ITC", "n_ITC", "interest rate", "Design completion", "Design_Maturity_0",
  "supply chain exp_0", "N supply chain", "Const Proficiency", "N const prof", "AE",
  "N AE prof", "standardization", "modularity", "BOP commercial", "RB Safety Related",
]

def unpack_sample_column(col_vec):
    # col_vec length must match LEVER_ORDER
    return dict(zip(LEVER_ORDER, col_vec))
