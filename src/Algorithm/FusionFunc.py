import numpy as np
from .Algorithm import Algorithm

class FusionFunc(Algorithm):
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
    #acc2211: FIRST WALL COST
    def acc2211(ife, ucfwa, ucfws, fwarea, ucfwps, ucblss, fwmatm, uccarb, ucblli2o, ucconc, ifueltyp, fwallcst,lsa):
        cmlsa = [0.5000e0, 0.7500e0, 0.8750e0, 1.0000e0]
        lsa=int(lsa)
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
        cmlsa = [0.6700e0, 0.8350e0, 0.9175e0, 1.0000e0]
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
            acc22131 = (1.0e-6 * cmlsa[lsa - 1] * ucshld * (shmatm + shmatm + shmatm)
                        + uccarb *   (shmatm+ shmatm + shmatm)
                        + ucblli2o * (shmatm+ shmatm + shmatm)
                        + ucconc *   (shmatm+ shmatm + shmatm))
        else:
            acc22131 = 1.0e-6 * whtshld * ucshld * cmlsa[lsa - 1]
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
        return acc22132

    @staticmethod
    #acc2214: TOTAL SUPPORT STRUCTURE COST
    def acc2214(gsmass, ucgss, lsa):
        lsa=int(lsa)
        cmlsa = [0.6700e0, 0.8350e0, 0.9175e0, 1.0000e0]
        acc2214 = 1.0e-6 * gsmass * ucgss * cmlsa[lsa - 1]
        return acc2214

    @staticmethod
    #acc2215: DIVERTOR COST
    def acc2215(ife, divsur, ucdiv, ifueltyp, divcst):
        if ife != 1:
            acc2215 = 1.0e-6 * divsur * ucdiv
            acc2215 = acc2215
            if ifueltyp == 1:
                divcst = acc2215
                acc2215 = 0.0e0
            elif ifueltyp == 2:
                divcst = acc2215
            else:
                divcst = 0.0e0
        else:
            acc2215 = 0.0e0
            divcst = 0.0e0
        #NOTE: divcst is not used in the original code but is included in the function signature
        return acc2215

    @staticmethod
    #acc22211: TF COIL CONDUCTOR COST
    def acc22211(whtcp, uccpcl1, itart, ifueltyp, cpstcst, whtconsc, 
                tfleng, n_tf_turn, uccu, whtconcu, cconshtf, cconfix, n_tf, lsa, i_tf_sup,
                ucsc_0, ucsc_1, ucsc_2, ucsc_3, ucsc_4, ucsc_5, ucsc_6, ucsc_7, ucsc_8,
                fkind, i_tf_sc_mat):
        lsa=int(lsa)
        i_tf_sc_mat = int(i_tf_sc_mat)
        i_tf_sup = int(i_tf_sup)
        ifueltyp = int(ifueltyp)
        itart = int(itart)
        cmlsa = [0.6900e0, 0.8450e0, 0.9225e0, 1.0000e0]
        ucsc = np.array([ucsc_0, ucsc_1, ucsc_2, ucsc_3, ucsc_4, ucsc_5, ucsc_6, ucsc_7, ucsc_8])
        if i_tf_sup == 1:  
            costtfsc = ucsc[i_tf_sc_mat - 1]*whtconsc/(tfleng*n_tf_turn)
            costtfcu = uccu*whtconcu/(tfleng*n_tf_turn)
            costwire = costtfsc+costtfcu
            ctfconpm = costwire+cconshtf+cconfix
            acc22211 = 1.0e-6*ctfconpm*n_tf*tfleng*n_tf_turn
            acc22211 = fkind*acc22211*cmlsa[lsa - 1]
        else:  
            acc22211 = 1.0e-6*whtcp*uccpcl1*cmlsa[lsa - 1]
            acc22211 = fkind*acc22211
            if (itart == 1) and (ifueltyp == 1):
                acc22211 = cpstcst
                acc22211 = 0.0e0
            elif (itart == 1) and (ifueltyp == 2):
                acc22211 = cpstcst
        return acc22211

    @staticmethod
    #acc22212: TF COIL WINDING COST
    def acc22212(whttflgs, uccpclb, lsa, ucwindtf, n_tf, tfleng, n_tf_turn,i_tf_sup):
        lsa=int(lsa)
        cmlsa = [0.6900e0, 0.8450e0, 0.9225e0, 1.0000e0]
        if i_tf_sup == 1:
            acc22212 = 1.0e-6 * ucwindtf * n_tf * tfleng * n_tf_turn
            acc22212 = acc22212 * cmlsa[lsa - 1]
        else:
            acc22212 = 1.0e-6 * whttflgs * uccpclb * cmlsa[lsa - 1]
        return acc22212

    @staticmethod
    #acc22213: TF COIL CASE COST
    def acc22213(whtcas, uccase, n_tf, lsa, i_tf_sup):
        cmlsa = [0.6900e0, 0.8450e0, 0.9225e0, 1.0000e0]
        lsa=int(lsa)
        if i_tf_sup == 1:
            acc22213 = 1.0e-6 * (whtcas * uccase) * n_tf
            acc22213 = acc22213 * cmlsa[lsa - 1]
        else:
            acc22213 = 0
        return acc22213

    @staticmethod
    #acc22214: TF INTERCOIL STRUCTURE COST
    def acc22214(aintmass, ucint, lsa, i_tf_sup):
        cmlsa = [0.6900e0, 0.8450e0, 0.9225e0, 1.0000e0]
        lsa=int(lsa)
        if i_tf_sup == 1:
            acc22214 = 1.0e-6 * aintmass * ucint
            acc22214 = acc22214 * cmlsa[lsa - 1]
        else:
            acc22214 = 0
        return acc22214

    @staticmethod
    #acc22215: TF COIL GRAVITY SUPPORT STRUCTURE
    def acc22215(clgsmass, ucgss, lsa, i_tf_sup):
        cmlsa = [0.6900e0, 0.8450e0, 0.9225e0, 1.0000e0]
        lsa=int(lsa)
        if i_tf_sup == 1:
            acc22215 = 1.0e-6 * clgsmass * ucgss
            acc22215 = acc22215 * cmlsa[lsa - 1]
        else:
            acc22215 = 0
        return acc22215

    @staticmethod
    #acc22221: PF COIL CONDUCTOR COST
    def acc22221(ipfres, cconshpf, iohcl, nohc, 
                 ucsc_0, ucsc_1, ucsc_2, ucsc_3, ucsc_4, ucsc_5, ucsc_6, ucsc_7, ucsc_8, 
                 isumatpf, fcupfsu, vf, 
                 ric_0, ric_1, ric_2, ric_3, ric_4, ric_5, ric_6, turns_0, 
                 turns_1, turns_2, turns_3, turns_4, turns_5, turns_6, 
                 rjconpf_0, rjconpf_1, rjconpf_2, rjconpf_3, rjconpf_4, rjconpf_5, rjconpf_6, rjconpf_7, 
                 dcond_0, dcond_1, dcond_2, dcond_3, dcond_4, dcond_5, dcond_6, dcond_7, dcond_8, 
                 uccu, dcopper, cconfix, twopi, 
                 rpf_0, rpf_1, rpf_2, rpf_3, rpf_4, rpf_5, rpf_6, lsa, isumatoh, awpoh, vfohc, fcuohsu):

        ric = np.array([ric_0, ric_1, ric_2, ric_3, ric_4, ric_5, ric_6])
        turns = np.array([turns_0, turns_1, turns_2, turns_3, turns_4, turns_5, turns_6])
        cmlsa = [0.6900e0, 0.8450e0, 0.9225e0, 1.0000e0]
        pfwndl = 0
        ucsc=np.array([ucsc_0, ucsc_1, ucsc_2, ucsc_3, ucsc_4, ucsc_5, ucsc_6, ucsc_7, ucsc_8])
        dcond=np.array([dcond_0, dcond_1, dcond_2, dcond_3, dcond_4, dcond_5, dcond_6, dcond_7, dcond_8])
        rjconpf = np.array([rjconpf_0, rjconpf_1, rjconpf_2, rjconpf_3, rjconpf_4, rjconpf_5, rjconpf_6, rjconpf_7])
        rpf = np.array([rpf_0, rpf_1, rpf_2, rpf_3, rpf_4, rpf_5, rpf_6])
        lsa = int(lsa)
        isumatpf = int(isumatpf)
        isumatoh = int(isumatoh)
        nohc = int(nohc)
        for i in range(0, nohc):
            pfwndl = (pfwndl + twopi*rpf[i]*turns[i])
        if ipfres == 1:
            costpfsh = 0
        else: 
            costpfsh = cconshpf 
        if iohcl == 1:
            npf = nohc - 1
        else:
            npf = nohc
        acc22221 = 0
        for i in range(0, npf):
            if ipfres == 0:
                costpfsc = (ucsc[isumatpf - 1]*(1- fcupfsu)*(1-vf)*abs(ric[i]/turns[i])*1E6)/rjconpf[i]*dcond[isumatpf-1]
            else:
                costpfsc = 0
            if ipfres == 0:
                costpfcu = (uccu*fcupfsu*(1-vf)*abs(ric[i]/turns[i])*1E6)/rjconpf[i]*dcopper
            else:
                costpfcu = (uccu*(1-vf)*abs(ric[i]/turns[i])*1E6)/rjconpf[i]*dcopper

            costwire = costpfsc + costpfcu 
            cpfconpm = costwire+costpfsh+cconfix
            acc22221 = acc22221 +(1E-6*twopi*rpf[i]*turns[i]*cpfconpm)
        if iohcl == 1:
            if ipfres == 0:
                costpfsc = (ucsc[isumatoh -1]*awpoh*(1-vfohc)*(1-fcuohsu)/turns[nohc-1]*dcond[isumatoh-1])
            else:
                costpfsc = 0
            if ipfres ==0:
                costpfcu = (uccu*awpoh*(1-vfohc)*fcuohsu)/turns[nohc-1]*dcopper
            else:
                costpfcu = uccu*awpoh*(1-vfohc)/turns[nohc-1]*dcopper

            costwire = costpfsc + costpfcu
            cpfconpm = costwire +costpfsh +cconfix
            acc22221 = acc22221+(1E-6*twopi*rpf[nohc-1]*turns[nohc-1]*cpfconpm)
        acc22221 = acc22221*cmlsa[lsa-1]
        return acc22221

    @staticmethod
    #acc22222: PF COIL WINDING COST
    def acc22222(ucwindpf, lsa, twopi, rpf_0, rpf_1, rpf_2, rpf_3, rpf_4, rpf_5, rpf_6, turns_0, turns_1, turns_2, turns_3, turns_4, turns_5, turns_6, nohc):
        turns = np.array([turns_0, turns_1, turns_2, turns_3, turns_4, turns_5, turns_6])
        rpf = np.array([rpf_0, rpf_1, rpf_2, rpf_3, rpf_4, rpf_5, rpf_6])
        cmlsa = [0.6900e0, 0.8450e0, 0.9225e0, 1.0000e0]
        lsa=int(lsa)
        pfwndl = 0
        nohc = int(nohc)
        for i in range(0, nohc):
            pfwndl = pfwndl + (twopi * rpf[i] * turns[i])
        acc22222 = 1.0e-6 * ucwindpf * pfwndl
        acc22222 = acc22222 * cmlsa[lsa - 1]
        return acc22222

    @staticmethod
    #acc22223: PF COIL CASE COST
    def acc22223(uccase, whtpfs, lsa):
        cmlsa = [0.6900e0, 0.8450e0, 0.9225e0, 1.0000e0]
        lsa=int(lsa)
        acc22223 = 1.0e-6 * uccase * whtpfs
        acc22223 = acc22223 * cmlsa[lsa - 1]
        return acc22223

    @staticmethod
    #acc22224: PF COIL SUPPORT STRUCTURE COST
    def acc22224(ucfnc, fncmass, lsa):
        cmlsa = [0.6900e0, 0.8450e0, 0.9225e0, 1.0000e0]
        lsa=int(lsa)
        acc22224 = 1.0e-6 * ucfnc * fncmass
        acc22224 = acc22224 * cmlsa[lsa - 1]
        return acc22224

    @staticmethod
    #acc2223: VACUUM VESSEL ASSEMBLY COST 
    def acc2223(vvmass, uccryo, lsa):
        cmlsa = [0.6900e0, 0.8450e0, 0.9225e0, 1.0000e0]
        lsa=int(lsa)
        acc2223 = 1.0e-6 * vvmass * uccryo
        acc2223 = acc2223 * cmlsa[lsa - 1]
        return acc2223

    @staticmethod
    #acc2231: ECH SYSTEM COST
    def acc2231(ucech, echpwr, exprf, ifedrv, dcdrv1, dcdrv2, cdriv1, 
                mcdriv, edrive, etadrv, dcdrv0, cdriv0 ,cdriv3, fcdfuel, 
                ife, cdriv2,ifueltyp):
        exprf = 1.0e0
        if ife == 1 :
            if ifedrv == 2:
                if dcdrv1 <= dcdrv2:
                    switch = 0.0e0
                else:
                    switch = (cdriv2 - cdriv1) / (dcdrv1 - dcdrv2)
                if edrive <= switch:
                    acc2231 = mcdriv * (cdriv1 + dcdrv1 * 1.0e-6 * edrive)
                else:
                    acc2231 = mcdriv * (cdriv2 + dcdrv2 * 1.0e-6 * edrive)
            elif ifedrv == 3:
                acc2231 = (mcdriv * 1.0e-6 * cdriv3 * (edrive / etadrv))
            else:
                acc2231 = mcdriv * (cdriv0 + (dcdrv0 * 1.0e-6 * edrive))
            if ifueltyp == 1:
                    acc2231 = (1.0e0 - fcdfuel) * acc2231
        else:
            acc2231 = ((1.0e-6 * ucech) * ((1.0e6 * echpwr) ** exprf))
            if ifueltyp == 1:
                acc2231 = (1.0e0 - fcdfuel) * acc2231
        return acc2231

    @staticmethod
    #acc2232: LOWER HYBRID SYSTEM COST
    def acc2232(iefrf, uclh, plhybd, exprf, ucich, fcdfuel, ifueltyp, ife):
        exprf = 1.0e0
        if ife != 1:
            if iefrf != 2:
                acc2232 = (1.0e-6 * uclh * (1.0e6 * plhybd) ** exprf)
            else:
                acc2232 = (1.0e-6 * ucich * (1.0e6 * plhybd) ** exprf)
            if ifueltyp == 1:
                acc2232 = (1.0e0 - fcdfuel) * acc2232
        else:
            if ifueltyp == 1:   
                acc2232 = 0.0e0
        return acc2232

    @staticmethod
    #acc2233: NEUTRAL BEAM SYSTEM COST 
    def acc2233(ucnbi, exprf, fcdfuel, ifueltyp, pnbitot, ife, ifedrv):
        if ife == 1:
            acc2233 = (1.0e-6 * ucnbi * (1.0e6 * pnbitot) ** exprf)
            if ifueltyp == 1:
                acc2233 = (1.0e0 - fcdfuel) * acc2233
                acc2233 = acc2233
        else:
            if ifedrv == 2:
                acc2233 = 0.0e0
            else:
                acc2233 = 0.0e0
        return acc2233

    @staticmethod
    #acc2241: HIGH VACUUM PUMPS COST 
    def acc2241(vpumpn, uccpmp, uctpmp, ntype):
        if ntype == 1:
            acc2241 = 1.0e-6 * vpumpn * uccpmp
        else:
            acc2241 = 1.0e-6 * vpumpn * uctpmp
        return acc2241

    @staticmethod
    #acc2242: BACKING PUMPS COST
    def acc2242(nvduct, ucbpmp):
        acc2242 = 1.0e-6 * nvduct * ucbpmp
        acc2242 = acc2242 
        return acc2242

    @staticmethod
    #acc2243: VACUUM DUCT COST
    def acc2243(nvduct, dlscal, ucduct):
        acc2243 = 1.0e-6 * nvduct * dlscal * ucduct
        return acc2243

    @staticmethod
    #acc2244: VALVES COST
    def acc2244(nvduct, vcdimax, ucvalv):
        acc2244 = 1.0e-6 * 2.0e0 * nvduct * ((vcdimax * 1.2e0) ** 1.4e0) * ucvalv
        return acc2244

    @staticmethod
    #acc2245: DUCT SHEILDING COST 
    def acc2245(nvduct, vacdshm, ucvdsh):
        acc2245 = 1.0e-6 * nvduct * vacdshm * ucvdsh
        return acc2245

    @staticmethod
    #acc2246: INSTRUMENTATION COST
    def acc2246(ucviac):
        acc2246 = 1.0e-6 * ucviac
        return acc2246

    @staticmethod
    #acc22511: TF COIL POWER SUPPLIED COST
    def acc22511(uctfps, tfckw, tfcmw, expel):
        acc22511 = 1.0e-6 * uctfps * (tfckw * 1.0e3 + tfcmw * 1.0e6) ** expel
        return acc22511

    @staticmethod
    #acc22512: TF COIL BREAKERS COST
    def acc22512(uctfbr, n_tf, cpttf, vtfskv, expel, uctfsw, i_tf_sup):
        if i_tf_sup == 1:
            acc22512 = 1.0e-6 * (uctfbr * n_tf * (cpttf * vtfskv * 1.0e3) ** expel + uctfsw * cpttf)
        else:
            acc22512 = 0.0e0
        return acc22512

    @staticmethod
    #acc22513: TF COIL DUMP RESISTORS COST 
    def acc22513(uctfdr, estotftgj, uctfgr, n_tf):
        acc22513 = 1.0e-6 * (1.0e9 * uctfdr * estotftgj + uctfgr * 0.5e0 * n_tf)
        return acc22513

    @staticmethod
    #acc22514: TF COIL INSTRUMENTATION AND CONTROL
    def acc22514(uctfic, n_tf):
        acc22514 = 1.0e-6 * uctfic * (30.0e0 * n_tf)
        return acc22514

    @staticmethod
    #acc22515: TF COIL BUSSING COST
    def acc22515(uctfbus, tfbusmas, ucbus, cpttf, tfbusl, i_tf_sup):
        if i_tf_sup == 1:
            acc22515 = 1.0e-6 * ucbus * cpttf * tfbusl
        else:
            acc22515 = 1.0e-6 * uctfbus * tfbusmas
        return acc22515

    @staticmethod
    #acc22521: PF COIL POWER SUPPLIES COST
    def acc22521(ucpfps, peakmva):
        acc22521 = 1.0e-6 * ucpfps * peakmva
        return acc22521

    @staticmethod
    #acc22522: PF COIL INSTRUMENTATION AND CONTROL 
    def acc22522(ucpfic, pfckts):
        acc22522 = 1.0e-6 * ucpfic * pfckts * 30.0e0
        return acc22522

    @staticmethod
    #acc22523: PF COIL BUSSING COST
    def acc22523(ucpfb, spfbusl, acptmax):
        acc22523 = 1.0e-6 * ucpfb * spfbusl * acptmax
        return acc22523

    @staticmethod
    #acc22524: PF COIL BURN POWER SUPPLIES COST 
    def acc22524(ucpfbs, pfckts, srcktpm):
        if pfckts == 0:
            acc22524 = 0.0e0
        else:
            acc22524 = 1.0e-6 * ucpfbs * pfckts * (srcktpm / pfckts) ** 0.7e0
        return acc22524

    @staticmethod
    #acc22525: PF COIL BREAKERS COST   
    def acc22525(ucpfbk, pfckts, acptmax, vpfskv):
        acc22525 = 1.0e-6 * ucpfbk * pfckts * ((acptmax * vpfskv) ** 0.7e0)
        return acc22525

    @staticmethod
    #acc22526: PF COIL DUMP RESISTORS COST
    def acc22526(ucpfdr1, ensxpfm):
        acc22526 = 1.0e-6 * ucpfdr1 * ensxpfm
        return acc22526

    @staticmethod
    #acc22527: PF COIL AC BREAKER COST
    def acc22527(ucpfcb, pfckts):
        acc22527 = 1.0e-6 * ucpfcb * pfckts
        return acc22527

    @staticmethod
    #acc2253: TOTAL ENERGY STORAGE COST
    def acc2253(lpulse, istore, ucblss, pthermmw, tdown, dtstor, pnetelmw):
        acc2253 = 0.0e0
        if lpulse == 1:
            if istore == 1:
                acc2253 = 0.1e0
                acc2253 = acc2253 + 0.8e0
                acc2253 = acc2253 + 4.0e0
                acc2253 = acc2253 + 0.5e0
                acc2253 = acc2253 + 2.8e0
                acc2253 = acc2253 + 29.0e0
            elif istore == 2:
                acc2253 = 0.1e0
                acc2253 = acc2253 + 0.8e0
                acc2253 = acc2253 + 2.8e0
                acc2253 = acc2253 + 4.0e0
                acc2253 = acc2253 + 330.0e0
                acc2253 = acc2253 + 1.0e0
                acc2253 = acc2253 + 2.0e0
                acc2253 = acc2253 + 18.0e0
            elif istore == 3:
                shcss = 520.0e0
                acc2253 = ucblss * (pthermmw * 1.0e6) * tdown / (shcss * dtstor)
        if istore < 3:
            acc2253 = acc2253 * pnetelmw / 1200.0e0
            acc2253 = acc2253 * 1.36e0
        return acc2253

    @staticmethod
    #accpp: PUMPS AND PIPING SYSTEM COST 
    def acc22612(uchts_0, uchts_1, coolwh, pfwdiv, exphts, pnucblkt, pnucshld, lsa):
        uchts= np.array([uchts_0, uchts_1])
        lsa=int(lsa)
        cmlsa = [0.4000e0, 0.7000e0, 0.8500e0, 1.0000e0]
        accpp = 1.0e-6 * uchts[coolwh - 1] * ((1.0e6 * pfwdiv) ** exphts +
                                            (1.0e6 * pnucblkt) ** exphts + (1.0e6 * pnucshld) ** exphts)
        accpp = accpp * cmlsa[lsa - 1]
        return accpp

    @staticmethod
    #acchx: PRIMARY HEAT EXCHANGER COST
    def acc22611(ucphx, nphx, pthermmw, exphts, lsa):
        cmlsa = [0.4000e0, 0.7000e0, 0.8500e0, 1.0000e0]
        acchx = 1.0e-6 * ucphx * nphx * (1.0e6 * pthermmw / nphx) ** exphts
        acchx = acchx * cmlsa[lsa - 1]
        return acchx
    
    @staticmethod
    def acc2262(ucahts, pinjht, exphts, crypmw, vachtmw, trithtmw, fachtmw, ife, tdspmw, tfacmw, lsa):
        lsa=int(lsa)
        cmlsa = [0.4000e0, 0.7000e0, 0.8500e0, 1.0000e0]
        acccppa = (1.0e-6*ucahts*((1.0e6*pinjht)**exphts+(1.0e6*crypmw)**exphts+
                    (1.0e6*vachtmw)**exphts+(1.0e6*trithtmw)**exphts+(1.0e6*fachtmw)**exphts))
        if ife == 1:
            acccppa = acccppa+1.0e-6*ucahts*((1.0e6*tdspmw)**exphts
                    + (1.0e6*tfacmw)**exphts)
        acccppa = acccppa*cmlsa[lsa - 1]
        return acccppa
    @staticmethod
    def acc2263(uccry, tmpcry, helpow, lsa, expcry):
        lsa=int(lsa)
        cmlsa = [0.4000e0, 0.7000e0, 0.8500e0, 1.0000e0]

        acc2263 = 1.0e-6*uccry*(4.5e0/tmpcry)*(helpow**expcry)
        acc2263 = acc2263*cmlsa[lsa - 1]
        return acc2263

    @staticmethod
    #acc2271: FUELING SYSTEM COST
    def acc2271(ucf1):
        acc2271 = 1.0e-6 * ucf1
        return acc2271

    @staticmethod
    #acc2272: FUEL PROCESS AND PURIFICATION COST 
    def acc2272(ife, rndfuel, afuel, umass, gain, edrive, fburn, reprat, ucfpr):
        if ife == 1:
            targtm = (gain * edrive * 3.0e0 * 1.67e-27 * 1.0e3) / (1.602e-19 * 17.6e6 * fburn)
            wtgpd = targtm * reprat * 86400.0e0
        else:
            wtgpd = 2.0e0 * rndfuel * afuel * umass * 1000.0e0 * 86400.0e0
        acc2272 = 1.0e-6 * ucfpr * (0.5e0 + 0.5e0 * (wtgpd / 60.0e0) ** 0.67e0)
        return acc2272

    @staticmethod
    #acc2273: ATMOSPHERIC RECOVERY SYSTEMS COST
    def acc2273(ftrit, ucdtc, volrci, wsvol):
        cfrht = 1.0e5
        if ftrit > 1.0e-3:
            acc2273 = (1.0e-6 * ucdtc * ((cfrht / 1.0e4) ** 0.6e0 * (volrci + wsvol)))
        else:
            acc2273 = 0.0e0
        return acc2273

    @staticmethod
    #acc2274: NUCLEAR BUILDING VENTILATION COST
    def acc2274(ucnbv, volrci, wsvol):
        acc2274 = 1.0e-6 * ucnbv * (volrci + wsvol) ** 0.8e0
        return acc2274

    @staticmethod
    #acc228: INSTRUMENTATION AND CONTROL COST
    def acc228(uciac):
        acc228 = 1.0e-6 * uciac
        return acc228

    @staticmethod
    #acc229: MAINTENANCE EQUIPMENT COST
    def acc229(ucme):
        acc229 = 1.0e-6 * ucme
        return acc229

    @staticmethod
    #acc23: TURBINE PLANT EQUIPMENT COST
    def acc23(ireactor, ucturb_0, ucturb_1, coolwh, pgrossmw, exptpe):
        ucturb = np.array([ucturb_0, ucturb_1])
        coolwh = int(coolwh)
        if ireactor == 1:
            acc23 = (1.0e-6 * ucturb[coolwh - 1] * (pgrossmw / 1200.0e0) ** exptpe)
        else:
            # NOTE : In the original code, this line was commented out.
            acc23 = (1.0e-6 * ucturb[coolwh - 1] * (pgrossmw / 1200.0e0) ** exptpe)
        return acc23

    @staticmethod
    #acc241: SWITCHYARD EQUIPMENT COST
    def acc241(ucswyd, lsa):
        cmlsa = [0.5700e0, 0.7850e0, 0.8925e0, 1.0000e0]
        lsa=int(lsa)    
        acc241 = 1.0e-6 * ucswyd * cmlsa[lsa - 1]
        return acc241

    @staticmethod
    #acc242: TRANSFORMERS COST
    def acc242(ucpp, pacpmw, expepe, ucap, fcsht, lsa):
        cmlsa = [0.5700e0, 0.7850e0, 0.8925e0, 1.0000e0]
        lsa=int(lsa)
        acc242 = 1.0e-6 * ((ucpp * (pacpmw * 1.0e3) ** expepe) + ucap * (fcsht * 1.0e3))
        acc242 = acc242 * cmlsa[lsa - 1]
        return acc242

    @staticmethod
    #acc243: LOW VOLTAGE EQUIPMENT COST
    def acc243(uclv, tlvpmw, lsa):
        cmlsa = [0.5700e0, 0.7850e0, 0.8925e0, 1.0000e0]
        lsa=int(lsa)
        acc243 = (1.0e-6
            * uclv
            * tlvpmw
            * 1.0e3
            / 0.8e0
            * cmlsa[lsa - 1]
        )
        return acc243

    @staticmethod
    #acc244: DIESEL BACKUP EQUIPMENT COST 
    def acc244(ucdgen, lsa):
        cmlsa = [0.5700e0, 0.7850e0, 0.8925e0, 1.0000e0]
        lsa=int(lsa)
        acc244 = 1.0e-6 * ucdgen * 4.0e0 * cmlsa[lsa - 1]
        return acc244

    @staticmethod
    #acc245: AUXILIARY FACILITIES COST
    def acc245(ucaf, lsa):
        cmlsa = [0.5700e0, 0.7850e0, 0.8925e0, 1.0000e0]
        lsa=int(lsa)
        acc245 = 1.0e-6 * ucaf * cmlsa[lsa - 1]
        return acc245

    @staticmethod
    #acc25: MISCELLANEOUS PLANT EQUIPMENT COST 
    def acc25(ucmisc, lsa):
        cmlsa = [0.7700e0, 0.8850e0, 0.9425e0, 1.0000e0]
        lsa=int(lsa)
        acc25 = 1.0e-6 * ucmisc * cmlsa[lsa - 1]
        return acc25

    @staticmethod
    #acc26: HEAT REJECTION SYSTEM COST
    def acc26(ireactor, powfmw, pinjwp, tfcmw, pthermmw, pgrossmw, uchrs, lsa):
        cmlsa = [0.8000e0, 0.9000e0, 0.9500e0, 1.0000e0]
        lsa=int(lsa)
        if ireactor == 0:
            pwrrej = powfmw + pinjwp + tfcmw
        else:
            pwrrej = pthermmw - pgrossmw
        acc26 = (1.0e-6 * uchrs * pwrrej) / 2300.0e0 * cmlsa[lsa - 1]
        return acc26
    
    @staticmethod
    #calelevol: ELECTRICAL EQUIPMENT BUILDING COST
    def calelevol(tfcbv, pfbldgm3, esbldgm3, pibv):
        calelevol = tfcbv + pfbldgm3 + esbldgm3 + pibv
        return calelevol

    @staticmethod
    #calaintmass: TF INTERCOIL STRUCTURE COST CALCULATION
    def calaintmass(ai, b0, tf_h_width):
        calaintmass = 1.4e6 * (ai / 2.2e7) * (b0 / 4.85e0) * (tf_h_width**2 / 50.0e0)
        return calaintmass

    @staticmethod
    #calclgsmass: CALCULATION OF TF COIL GRAVITY SUPPORT STRUCTURE
    def calclgsmass(coilmass, r0, dens, sigal):
        calclgsmass = coilmass * (r0 / 6.0e0) * 9.1e0 * 9.807e0 * (dens / sigal)
        return calclgsmass
    
    @staticmethod
    #calfncmass: PF COIL SUPPORT STRUCTURE COST CALCULATION
    def calfncmass(a, ai, akappa, r0):
        calfncmass = 2.1e-11 * ai * ai * r0 * akappa * a
        return calfncmass

    @staticmethod
    #calechpwr: ECH SYSTEM COST CALCULATION
    def calechpwr(faccd, faccdfix, plascur, effrfss, pheat):
        calechpwr = (1.0e-6* (faccd - faccdfix)* plascur / effrfss)+ pheat
        return calechpwr
    
    @staticmethod
    #caldlscal: VCUUM DUCT COST CALCULATION
    def caldlscal(l1, ltot, imax, d_0, d_1, d_2, d_3):
        imax = int(imax)
        d = np.array([d_0, d_1, d_2, d_3])
        caldlscal = l1 * d[imax] ** 1.4e0 + (ltot - l1) * (d[imax] * 1.2e0) ** 1.4e0
        return caldlscal
    
    @staticmethod
    #calgsmass: TOTAL SUPPORT STRUCTURE COST CALCULATION 
    def calgsmass(coolmass, fwmass, blmass, shldmass, dvrtmass, tfmass, pfmass, tfhmax, dens, sigal, aintmass, clgsmass,r0):
        ws1 = coolmass + fwmass + blmass + shldmass + dvrtmass
        gsm1 = 5.0e0 * 9.807e0 * ws1 * dens / sigal
        ws2 = ws1 + tfmass + pfmass + aintmass + clgsmass
        gsm2 = 1.0e-3 * 34.77e0 * (r0 + 1.0e0) * np.sqrt(0.001e0 * ws2) * dens
        gsm3 = 1.0e-6 * 0.3e0 * (tfhmax + 2.0e0) * ws2 * dens
        calgsmass = gsm1 + gsm2 + gsm3
        return calgsmass
    
    @staticmethod
    #calrbvol: REACTOR BUILDING VOLUME CALCULATION
    def calrbvol(wrbi, rbwt, drbi, hrbi, rbrt, fndt, rbvfac):
        rbw = 2.0e0 * wrbi + 2.0e0 * rbwt
        rbl = drbi + 2.0e0 * rbwt
        rbh = hrbi + rbrt + fndt
        calrbvol = rbvfac * rbw * rbl * rbh
        return calrbvol
    
    @staticmethod
    #calrndfuel: FUEL BURNUP RATE CALCUATION
    def calrndfuel(fusionrate, palpnb, ealphadt, echarge, vol):
        fusionrate = fusionrate + (1.0e6*palpnb)/ (1.0e3 * ealphadt * echarge* vol)
        fusrat= fusionrate*vol
        return fusrat
    
    @staticmethod
    #calvolrci: INTERNAL VOLUME OF REACTOR BUILDING CALCULATION
    def calvolrci(rbvfac, wrbi, drbi, hrbi):
        calvolrci = rbvfac * 2.0e0 * wrbi * drbi * hrbi
        return calvolrci
    
    @staticmethod
    #calrmbvol: VOLUME OF MAINTENANCE AND ASSEMBLY BUILDING CALCULATION 
    def calrmbvol(shro, shri, trcl, hcwt, hccl, wgt2, shmf, shm, n_tf, shh, stcl, mbvfac, fndt):
        tcw = shro - shri + 4.0e0 * trcl
        tcl = 5.0e0 * tcw + 2.0e0 * hcwt
        dcw = 2.0e0 * tcw + 1.0e0
        hcw = shro - shri + 3.0e0 * hccl + 2.0e0
        hcl = 3.0e0 * (shro - shri) + 4.0e0 * hccl + tcw
        rmbw = hcw + dcw + 3.0e0 * hcwt
        rmbl = hcl + 2.0e0 * hcwt
        if wgt2 > 1.0e0:
            wgts = wgt2
        else:
            wgts = shmf * shm / n_tf
        cran = 9.41e-6 * wgts + 5.1e0
        rmbh = (10.0e0 + shh+ trcl + cran+ stcl+ fndt)
        tch = shh + stcl + fndt
        calrmbvol = mbvfac * rmbw * rmbl * rmbh + tcw * tcl * tch
        return calrmbvol
    
    @staticmethod
    #calwsvol: VOLUME OF WARM SHOP BUILDING CALCULATION
    def calwsvol(shro, shri, trcl, hcwt, hccl, wgt2, shmf, shm, n_tf, shh, stcl, fndt, wsvfac):
        tcw = shro - shri + 4.0e0 * trcl
        hcw = shro - shri + 3.0e0 * hccl + 2.0e0
        hcl = 3.0e0 * (shro - shri) + 4.0e0 * hccl + tcw
        dcw = 2.0e0 * tcw + 1.0e0
        rmbw = hcw + dcw + 3.0e0 * hcwt
        rmbl = hcl + 2.0e0 * hcwt
        rmbw = hcw + dcw + 3.0e0 * hcwt
        wsa = (rmbw + 7e0)*20+(rmbl*7)
        if wgt2 > 1.0e0:
            wgts = wgt2
        else:
            wgts = shmf * shm / n_tf
        cran = 9.41e-6 * wgts + 5.1e0
        rmbh = (10.0e0 + shh+ trcl + cran+ stcl+ fndt)
        calwsvol = wsvfac*wsa*rmbh
        return calwsvol
    
    @staticmethod
    #calawpoh: PFCOIL CONDUCTOR COST CALCULATION
    def calawpoh(oh_steel_frac, areaoh):
        areaspf = oh_steel_frac * areaoh
        calawpoh = areaoh - areaspf
        return calawpoh
    
    @staticmethod
    #caltargtm: MASS OF FUEL CALCULATION
    def caltargtm(gain, edrive, fburn):
        caltargtm = (gain* edrive * 3.0e0 * 1.67e-27 * 1.0e3/ (1.602e-19 * 17.6e6 * fburn))
        return caltargtm
    
    @staticmethod
    #calwtgpd: MASS OF FUEL USED PER DAY
    def calwtgpd(targtm, reprat, rndfuel, afuel, umass, ife):
        ife = int(ife)
        if ife ==1:
            calwtgpd = targtm*reprat*86400
        else:
            calwtgpd = 2.0e0* rndfuel* afuel * umass* 1000.0e0* 86400.0e0
        return calwtgpd
    
    @staticmethod
    #fwbllife: FIRST WALL AND BLANKET OPERATIONAL LIFE
    def fwbllife(bktlife):
        fwbllife = bktlife
        return fwbllife
    
    @staticmethod
    #feffwbl: FIRST WALL AND BLANKET COMPOUND INTEREST FACTOR
    def feffwbl(discount_rate, fwbllife):
        feffwbl = (1+discount_rate)**fwbllife
        return feffwbl
    
    @staticmethod
    #crffwbl: FIRST WALL AND BLANKET CAPITAL RECOVERY FACTOR
    def crffwbl(feffwbl, discount_rate):
        crffwbl = (feffwbl * discount_rate) / (feffwbl - 1.0e0)
        return crffwbl
    
    @staticmethod
    #fefdiv: DIVERTOR COMPOUND INTEREST FACTOR
    def fefdiv(divlife, discount_rate, ife):
        ife = int(ife)
        if ife == 1:
            fefdiv = 0
        else:
            fefdiv = (1.0e0 + discount_rate) ** divlife
        return fefdiv
    
    @staticmethod
    #crfdiv: DIVERTOR CAPITAL RECOVERY FACTOR
    def crfdiv(fefdiv, discount_rate, ife):
        ife = int(ife)
        if ife == 1:
            crfdiv = 0
        else:
            crfdiv = (fefdiv * discount_rate) / (fefdiv - 1.0e0)
        return crfdiv
    
    @staticmethod
    #fefcp: CENTREPOST COMPOUND INTEREST FACTOR
    def fefcp(itart, ife, discount_rate, cplife):
        itart = int(itart)
        ife = int(ife)
        if (itart == 1) and (ife != 1):
            fefcp = (1.0e0 + discount_rate) ** cplife
        else:
            fefcp = 0
        return fefcp
    
    @staticmethod
    #crfcp: CENTREPOST CAPITAL RECOVERY FACTOR 
    def crfcp(itart, ife, fefcp, discount_rate):
        itart = int(itart)
        ife = int(ife)
        if (itart == 1) and (ife != 1):
            crfcp = (fefcp * discount_rate) / (fefcp - 1.0e0)
        else: 
            crfcp = 0
        return crfcp
    
    @staticmethod
    #fefcdr: CURRENT DRIVE SYSTEM COMPOUND INTEREST FACTOR
    def fefcdr(discount_rate, cdrlife):
        fefcdr = (1.0e0 + discount_rate) ** cdrlife
        return fefcdr
    
    @staticmethod
    #crfcdr: CURRENT DRIVE CAPITAL RECOVERY FACTOR 
    def crfcdr(fefcdr, discount_rate):
        crfcdr = (fefcdr * discount_rate) / (fefcdr - 1.0e0)
        return crfcdr