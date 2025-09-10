import numpy as np
from .Algorithm import Algorithm

class MsrFunc(Algorithm):
    def __init__(self, ind, alg_name, alg_for, alg_description, alg_formulation, alg_units, variables, constants):
        super().__init__(ind, alg_name, alg_for, alg_description, alg_formulation, alg_units, variables, constants)
    
    def run(self, inputs: dict) -> float:
        """
        Executes the algorithm specified by the name in the instance variables.
        
        Parameters:
        inputs (dict): Dictionary of input variables required for the algorithm.

        Returns:
        float: Result of the algorithm computation.
        """
        # run the algorithm use self.name not self.alg_name
        return self._run_algorithm(self.name, [inputs[var] for var in self.variables.split(",")])

    def _run_algorithm(self, alg_name: str, variables: list) -> float:
        """
        Runs the specified algorithm with given variables.
        
        Parameters:
        alg_name (str): The name of the algorithm to run.
        variables (list): List of input variables for the algorithm.

        Returns:
        float: Result of the algorithm computation.
        """
        try:
            algorithm = getattr(self, alg_name)
            return algorithm(*variables)
        except AttributeError:
            raise ValueError(f"Algorithm {alg_name} not found")

    @staticmethod
    #acc211: SITE IMPROVEMENTS, FACILITES, LAND
    def acc211(csi, lsa, cland):
        lsa=int(lsa)
        cmlsa=[0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc211 = csi * cmlsa[lsa - 1] + cland
        return acc211
    
    @staticmethod
    #acc212: REACTOR BUILDING COST
    def acc212(ucrb, rbvol, exprb, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc212 = (1.0e-6 * ucrb * rbvol) ** exprb * cmlsa[lsa - 1]
        return acc212

    @staticmethod
    #acc213: TURBINE BUILDING COST
    def acc213(ireactor, cturbb, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        if ireactor == 1:
            acc213 = cturbb * cmlsa[lsa - 1]
        else:
            acc213 = 0.0e0
        return acc213

    @staticmethod
    #acc2141: REACTOR MAINTENANCE BUILDING COST
    def acc2141(ucmb, rmbvol, exprb, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc2141 = 1.0e-6 * ucmb * rmbvol ** exprb * cmlsa[lsa - 1]
        return acc2141

    @staticmethod
    #acc2142: WARM SHOP COST
    def acc2142(ucws, wsvol, exprb, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc2142 = (1.0e-6 * ucws * wsvol) ** exprb * cmlsa[lsa - 1]
        return acc2142

    @staticmethod
    #acc215: TRITIUM BUILDING COST
    def acc215(uctr, triv, exprb, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc215 = ((1.0e-6 * uctr * triv) * exprb) * cmlsa[lsa - 1]
        return acc215

    @staticmethod
    #acc216: ELECTICAL EQUIPMENT BUILDING COST
    def acc216(ucel, elevol, exprb, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc216 = 1.0e-6 * ucel * elevol ** exprb * cmlsa[lsa - 1]
        return acc216

    @staticmethod
    #acc2171: ADDITIONAL BUILDINGS COST
    def acc2171(ucad, admvol, exprb, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc2171 = 1.0e-6 * ucad * admvol ** exprb * cmlsa[lsa - 1]
        return acc2171

    @staticmethod
    #acc2172: CONTROLROOM BUILDINGS COST
    def acc2172(ucconc, convol, exprb, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc2172 = 1.0e-6 * ucconc * convol ** exprb * cmlsa[lsa - 1]
        return acc2172

    @staticmethod
    #acc2173: SHOP AND WAREHOUSES COST
    def acc2173(ucsh, shovol, exprb, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc2173 = 1.0e-6 * ucsh * shovol ** exprb * cmlsa[lsa - 1]
        return acc2173

    @staticmethod
    #acc2174: CRYOGENIC BUILDING COST
    def acc2174(uccr, cryvol, exprb, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc2174 = 1.0e-6 * uccr * cryvol ** exprb * cmlsa[lsa - 1]
        return acc2174

    @staticmethod
    #acc2211: FIRST WALL COST (MSR specific - simplified)
    def acc2211(ife, ucfwa, ucfws, fwarea, ucfwps, ucblss, fwmatm, uccarb, ucblli2o, ucconc, ifueltyp, fwallcst, lsa):
        lsa=int(lsa)
        cmlsa = [0.5000e0, 0.7500e0, 0.8750e0, 1.0000e0]
        if ife == 1:
            acc2211 = (1.0e-6 * cmlsa[lsa - 1] * (ucblss * (fwmatm(1, 1) + fwmatm(2, 1) + fwmatm(3, 1))
                                                + uccarb * (fwmatm(1, 2) + fwmatm(2, 2) + fwmatm(3, 2))
                                                + ucblli2o * (fwmatm(1, 4) + fwmatm(2, 4) + fwmatm(3, 4))
                                                + ucconc * (fwmatm(1, 5) + fwmatm(2, 5) + fwmatm(3, 5))))
        else:
            acc2211 = (1.0e-6 * cmlsa[lsa - 1] * ((ucfwa + ucfws) * fwarea + ucfwps))
        acc2211 = acc2211
        if ifueltyp == 1:
            acc2211 = 0
            acc2211 = fwallcst
        elif ifueltyp == 2:
            fwallcst = acc2211
        else:
            fwallcst = 0.0e0
        return acc2211

    @staticmethod
    #acc22121: BLANKET BERYLLIUM COST
    def acc22121(ife, wtbllipb, ucbllipb, whtblbe, ucblbe, iblanket, lsa):
        lsa=int(lsa)
        cmlsa = [0.5000e0, 0.7500e0, 0.8750e0, 1.0000e0]
        if ife == 1:
            acc22121 = 0
        else:
            if iblanket == 4:
                acc22121 = 1.0e-6 * wtbllipb * ucbllipb
            else:
                acc22121 = 1.0e-6 * whtblbe * ucblbe
        acc22121 = acc22121 * cmlsa[lsa - 1]
        return acc22121

    @staticmethod
    #acc22122: BLANKET BREEDER MATERIAL COST
    def acc22122(whtblli, ucblli, whtblbreed, ucblbreed, wtblli2o, ucblli2o, iblanket, lsa, ife):
        lsa=int(lsa)
        cmlsa = [0.5000e0, 0.7500e0, 0.8750e0, 1.0000e0]
        if ife == 1:
            if iblanket == 4:
                acc22122 = 1.0e-6 * whtblli * ucblli
            else:
                if iblanket == 2:
                    acc22122 = 1.0e-6 * whtblbreed * ucblbreed
                else:
                    acc22122 = 1.0e-6 * wtblli2o * ucblli2o
        else:
            acc22122 = 1.0e-6 * wtblli2o * ucblli2o
        acc22122 = acc22122 * cmlsa[lsa - 1]
        return acc22122

    @staticmethod
    #acc22123: BLANKET STAINLESS STEEL COST
    def acc22123(whtblss, ucblss, lsa):
        lsa=int(lsa)
        cmlsa = [0.5000e0, 0.7500e0, 0.8750e0, 1.0000e0]
        acc22123 = 1.0e-6 * whtblss * ucblss
        acc22123 = acc22123 * cmlsa[lsa - 1]
        return acc22123

    @staticmethod
    #acc22124: BLANKET VANADIUM COST
    def acc22124(whtblvd, ucblvd, ife, lsa):
        lsa=int(lsa)
        cmlsa = [0.5000e0, 0.7500e0, 0.8750e0, 1.0000e0]
        if ife == 1:
            acc22124 = 1.0e-6 * whtblvd * ucblvd
        else:
            acc22124 = 0
        acc22124 = acc22124 * cmlsa[lsa - 1]
        return acc22124

    @staticmethod
    #acc22131: BULK SHIELD COST
    def acc22131(ife, whtshld, ucshld, lsa, shmatm, uccarb, ucblli2o, ucconc):
        lsa=int(lsa)
        cmlsa = [0.5000e0, 0.7500e0, 0.8750e0, 1.0000e0]
        if ife == 1:
            acc22131 = 1.0e-6 * cmlsa[lsa - 1] * ucshld * (shmatm(1, 0) + shmatm(2, 0) + shmatm(3, 0)) + uccarb * (shmatm(1, 1) + shmatm(2, 1) + shmatm(3, 1)) + ucblli2o * (shmatm(1, 1) + shmatm(2, 1) + shmatm(3, 1)) + ucconc * (shmatm(1, 1) + shmatm(2, 1) + shmatm(3, 1))
        else:
            acc22131 = 1.0e-6 * whtshld * ucshld * cmlsa[lsa - 1]
        acc22131 = acc22131
        return acc22131

    @staticmethod
    #acc22132: PENETRATION SHIELDING COST
    def acc22132(ife, wpenshld, ucpens, lsa):
        lsa=int(lsa)
        cmlsa = [0.5000e0, 0.7500e0, 0.8750e0, 1.0000e0]
        if ife == 1:
            acc22132 = 1.0e-6 * wpenshld * ucpens * cmlsa[lsa - 1]
        else:
            acc22132 = 1.0e-6 * wpenshld * ucpens * cmlsa[lsa - 1]
        acc22132 = acc22132
        return acc22132

    @staticmethod
    #acc2214: TOTAL SUPPORT STRUCTURE COST
    def acc2214(gsmass, ucgss, lsa):
        lsa=int(lsa)
        cmlsa = [0.5000e0, 0.7500e0, 0.8750e0, 1.0000e0]
        acc2214 = 1.0e-6 * gsmass * ucgss * cmlsa[lsa - 1]
        acc2214 = acc2214
        return acc2214

    @staticmethod
    #acc2215: DIVERTOR COST
    def acc2215(ife, divsur, ucdiv, ifueltyp, divcst, lsa):
        lsa=int(lsa)
        cmlsa = [0.5000e0, 0.7500e0, 0.8750e0, 1.0000e0]
        if ife == 1:
            acc2215 = 1.0e-6 * divsur * ucdiv * cmlsa[lsa - 1]
        else:
            acc2215 = 1.0e-6 * divsur * ucdiv * cmlsa[lsa - 1]
        acc2215 = acc2215
        if ifueltyp == 1:
            acc2215 = 0
            acc2215 = divcst
        elif ifueltyp == 2:
            divcst = acc2215
        else:
            divcst = 0.0e0
        return acc2215

    # Add more MSR-specific algorithms as needed...
    # For now, we'll use the same structure as fusion but with MSR-specific modifications

    @staticmethod
    #acc241: SWITCHYARD EQUIPMENT COST
    def acc241(ucswyd, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc241 = 1.0e-6 * ucswyd * cmlsa[lsa - 1]
        return acc241

    @staticmethod
    #acc242: TRANSFORMERS COST
    def acc242(ucpp, pacpmw, expepe, ucap, fcsht, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc242 = 1.0e-6 * ((ucpp * (pacpmw * 1.0e3) ** expepe) + ucap * (fcsht * 1.0e3))
        acc242 = acc242 * cmlsa[lsa - 1]
        return acc242

    @staticmethod
    #acc243: LOW VOLTAGE EQUIPMENT COST
    def acc243(uclv, tlvpmw, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc243 = 1.0e-6 * uclv * tlvpmw * cmlsa[lsa - 1]
        return acc243

    @staticmethod
    #acc244: DIESEL BACKUP EQUIPMENT COST 
    def acc244(ucdgen, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc244 = 1.0e-6 * ucdgen * 4.0e0 * cmlsa[lsa - 1]
        return acc244

    @staticmethod
    #acc245: AUXILIARY FACILITIES COST
    def acc245(ucaf, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc245 = 1.0e-6 * ucaf * cmlsa[lsa - 1]
        return acc245

    @staticmethod
    #acc25: MISCELLANEOUS PLANT EQUIPMENT COST 
    def acc25(ucmisc, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        acc25 = 1.0e-6 * ucmisc * cmlsa[lsa - 1]
        return acc25

    @staticmethod
    #acc26: HEAT REJECTION SYSTEM COST
    def acc26(ireactor, powfmw, pinjwp, tfcmw, pthermmw, pgrossmw, uchrs, lsa):
        lsa=int(lsa)
        cmlsa = [0.6800e0, 0.8400e0, 0.9200e0, 1.0000e0]
        if ireactor == 0:
            pwrrej = powfmw + pinjwp + tfcmw
        else:
            pwrrej = pthermmw - pgrossmw
        acc26 = (1.0e-6 * uchrs * pwrrej) / 2300.0e0 * cmlsa[lsa - 1]
        return acc26 