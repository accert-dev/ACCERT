import numpy as np
import pandas as pd
from .Algorithm import Algorithm

class LCOE(Algorithm):
    """
    Class to calculate the levelized cost of electricity (LCOE) for a fusion power plant.
    """

    def __init__(self, c, ut, accert):
        self.c = c
        self.ut = ut
        self.accert = accert
        self.ref_model = None
        self.acc_tabl = None
        self.var_tabl = None
        self.alg_tabl = None

    def setup_tables(self, Accert):
        self.ref_model = Accert.ref_model
        self.acc_tabl = Accert.acc_tabl
        self.var_tabl = Accert.var_tabl
        self.alg_tabl = Accert.alg_tabl

    def quote_variable_values(self, c, Accert):
        """Extract and quote variable values from accert inputs and assign them to the instance."""
        # Extract total cost
        for key in ['2', '221', '222', '223', '2212']:
            setattr(self, f'c{key}', Accert.extract_total_cost_on_name(c, key)[2])

        # Extract variables
        var_names = [
            'cowner', 'cfind_0', 'cfind_1', 'cfind_2', 'cfind_3', 'fcontng', 'fcap0', 'fcap0cp', 'fcr0',
            'ife', 'ifueltyp', 'lsa', 'cdcost', 'fcdfuel', 'cpstcst', 'crfcdr', 'crfcp', 'cplife', 'tlife',
            'decomf', 'discount_rate', 'dintrt', 'dtlife', 'divcst', 'crfdiv', 'divlife', 'ucfuel', 'pnetelmw',
            'fhe3', 'wtgpd', 'uche3', 'n_day_year', 'cfactr', 'reprat', 'uctarg', 'crffwbl', 'fwallcst','itart',
            'fwbllife', 'ucoam_0', 'ucoam_1', 'ucoam_2', 'ucoam_3', 'ucwst_0', 'ucwst_1', 'ucwst_2', 'ucwst_3',
            'tburn', 'tcycle'
        ]
        for name in var_names:
            setattr(self, name, Accert.extract_variable_info_on_name(c, name)[0])

    def coelc(self):
        """Compute total cost of electricity (coe)."""
        # Inputs
        # get the values from the instance
        pnet = self.pnetelmw
        lsa = int(self.lsa)
        ife = int(self.ife)
        ifueltyp = int(self.ifueltyp)
        cfind = [self.cfind_0, self.cfind_1, self.cfind_2, self.cfind_3][lsa - 1]
        kwhpy = 1e3 * pnet * 24 * self.n_day_year * self.cfactr
        if ife != 1:
            kwhpy *= self.tburn / self.tcycle
        # Capital cost
        rctcore = self.c221 + self.c222 + self.c223
        cindrt = cfind * self.c2*(1.0e0 + self.cowner)
        ccont = self.fcontng*( self.c2+cindrt)
        concost = self.c2+ccont+cindrt
        moneyint = concost * (self.fcap0 - 1)
        capcost = concost + moneyint


        anncap = capcost * self.fcr0
        coecap = 1e9 * anncap / kwhpy/ 1e6

        # First wall/blanket
        if ifueltyp == 1 or ifueltyp == 2:
            blk = self.c2212
        else:
            blk = 0
        crffwbl = ((1 + self.discount_rate)**self.fwbllife) / (((1 + self.discount_rate)**self.fwbllife) - 1) * self.discount_rate
        annfwbl = (self.fwallcst + blk) * (1 + cfind) * self.fcap0cp * crffwbl
        if ifueltyp == 2:
            annfwbl *= 1 - self.fwbllife / self.tlife
        coefwbl = 1e9 * annfwbl / kwhpy / 1e6

        # Divertor
        if ife == 1:
            anndiv = coediv = 0
        else:
            crfdiv = ((1 + self.discount_rate)**self.divlife) / (((1 + self.discount_rate)**self.divlife) - 1) * self.discount_rate
            anndiv = self.divcst * (1 + cfind) * self.fcap0cp * crfdiv
            if ifueltyp == 2:
                anndiv *= 1 - self.divlife / self.tlife
            coediv = 1e9 * anndiv / kwhpy

        # Centrepost
        # Assuming `self.itart` is available or hardcoded for now as 1
        itart = self.itart
        if itart == 1 and ife != 1:
            crfcp = ((1 + self.discount_rate)**self.cplife) / (((1 + self.discount_rate)**self.cplife) - 1) * self.discount_rate
            anncp = self.cpstcst * (1 + cfind) * self.fcap0cp * crfcp
            if ifueltyp == 2:
                anncp *= 1 - self.cplife / self.tlife
            coecp = 1e9 * anncp / kwhpy
        else:
            anncp = coecp = 0

        # Current drive
        if ifueltyp == 0:
            anncdr = coecdr = 0
        else:
            crfcdr = ((1 + self.discount_rate)**self.tlife) / (((1 + self.discount_rate)**self.tlife) - 1) * self.discount_rate
            anncdr = self.cdcost * self.fcdfuel / (1 - self.fcdfuel) * (1 + cfind) * self.fcap0cp * crfcdr
            coecdr = 1e9 * anncdr / kwhpy

        # O&M cost
        ucoam = [self.ucoam_0, self.ucoam_1, self.ucoam_2, self.ucoam_3]
        annoam = ucoam[lsa - 1] * np.sqrt(pnet / 1200)
        coeoam = 1e9 * annoam / kwhpy

        # Fuel
        if ife == 1:
            annfuel = 1e-6 * self.uctarg * self.reprat * 3.1536e7 * self.cfactr
        else:
            annfuel = self.ucfuel * pnet / 1200 + 1e-6 * self.fhe3 * self.wtgpd * 1e-3 * self.uche3 * self.n_day_year * self.cfactr
        coefuel = 1e9 * annfuel / kwhpy

        # Waste
        ucwst = [self.ucwst_0, self.ucwst_1, self.ucwst_2, self.ucwst_3]
        annwst = ucwst[lsa - 1] * np.sqrt(pnet / 1200)
        coewst = 1e9 * annwst / kwhpy

        # Decommissioning
        anndecom = (
            self.decomf * concost * self.fcr0 /
            (1 + self.discount_rate - self.dintrt)**(self.tlife - self.dtlife)
        )
        coedecom = 1e9 * anndecom / kwhpy / 1e6

        # Aggregate
        coefuelt = coefwbl + coediv + coecdr + coecp + coefuel + coewst
        coe = coecap + coefuelt + coeoam + coedecom

        # Store results
        self.coecap = coecap
        self.coefuelt = coefuelt
        self.coeoam = coeoam
        self.coe = coe
        self.coetabl = [
            ['coecap', 'Cost of electricity due to plant capital cost ($/MWh)',coecap],
            ['coecdr', 'Cost of electricity due to current drive system replacements ($/MWh)',coecdr],
            ['coecp', 'Cost of electricity due to centrepost replacements ($/MWh)',coecp],
            ['coediv', 'Cost of electricity due to divertor renewal ($/MWh)',coediv],
            ['coefuel', 'Cost of electricity due to reactor fuel ($/MWh)',coefuel],
            ['coefuelt', 'Total cost of electricity due to "fuel-like" components ($/MWh)',coefuelt],
            ['coeoam', 'Cost of electricity due to operation and maintenance ($/MWh)',coeoam],
            ['coewst', 'Cost of electricity due to waste disposal ($/MWh)',coewst],
            ['coedecom', 'Cost of electricity due to decommissioning ($/MWh)',coedecom],
            ['coe', 'Total cost of electricity ($/MWh)',coe]
        ]

    def generate_excel(self):
        """Generate an Excel file with the results."""
        # Assuming self.alg_tabl is a DataFrame or similar structure
        # You can use pandas to write to Excel
        import pandas as pd

        # Create a DataFrame from the algorithm table
        df = pd.DataFrame(self.coetabl, columns=['Variable', 'Description', 'Value'])
        # Save to Excel
        df.to_excel('{}_LCOE_results.xlsx'.format(self.ref_model), index=False)
        print("Successfully created excel file {}_LCOE_results.xlsx".format(self.ref_model))
