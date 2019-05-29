import numpy as np
import pandas as pd
import scipy.constants as spc 
from scipy.special import ellipk

class CPWCalcs:
    
    def __init__(self,w,s,l,fo,er,h=None,t=0,pen_depth=None):
        self.__w = w
        self.__s = s
        self.__l = l
        self.__fo = fo
        self.__er = er
        self.__h = h
        self.__t = t
        self.__pen_depth=pen_depth
        
        if not self.__h:
            self.__eeff = (er + 1) /2
        elif self.__h:
            self.__eeff = self.effective_permittivity()
    
    def elliptic_integral(self,h=None):
        # Calculate the complete elliptic integral of the first kind
        if not self.__h:
            k = self.__w / (self.__w + 2*self.__s)
            kp = np.sqrt(1-k**2)
        elif self.__h:            
            k = ( np.sinh((np.pi*self.__w)/(4*self.__h)) 
                 / np.sinh( (np.pi*(self.__w+2*self.__s)) 
                           / (4*self.__h) ) )
            kp = np.sqrt(1-k**2)
        Kk = ellipk(k)
        Kkp = ellipk(kp)
        return (Kk,Kkp)

    def effective_permittivity(self):
        Kk1,Kkp1 = self.elliptic_integral()
        Kk2,Kkp2 = self.elliptic_integral(h=self.__h)
        
        eeff = 1 + .5*(self.__er-1) * Kk2/Kkp2 * Kkp1/Kk1
        return eeff
        
    def g(self):
        w = self.__w
        s = self.__s
        t = self.__t
        
        k = (w) / (w+(2*s))
        Kk,Kkp = self.elliptic_integral()
        
        outer = 1 / (2*(k**2)*(Kk**2))
        inner1 = -np.log(t / (4*w)) 
        inner2 = - (w/(w+(2*s))) * np.log(t / (4*(w+2*s)) )
        inner3 = (2*(w+s)/(w+(2*s))) * np.log(s / (w+s))
        inner = inner1 + inner2 + inner3
        g = outer * inner
        return g
    
    def Lk(self):
        Lk = (spc.mu_0 * ((self.__pen_depth**2)
                /(self.__t*self.__w)) * self.g())
        return Lk
    
    def Ltotal(self):
        return self.Lk() + self.inductance_per_length()
        
    def inductance_per_length(self):
        Kk,Kkp = self.elliptic_integral()
        return (spc.mu_0/4) * Kkp / Kk

    def capacitance_per_length(self):
        Kk,Kkp = self.elliptic_integral()
        return 4*spc.epsilon_0*self.__eeff*(Kk / Kkp)

    def impedance(self):
        Kk,Kkp = self.elliptic_integral()
        return ( ( 30 * np.pi ) / np.sqrt(self.__eeff) ) * (Kkp / Kk)

    def phase_velocity(self):
        Ll = self.inductance_per_length()
        Cl = self.capacitance_per_length()
        return 1 / np.sqrt(Ll*Cl)

    def phase_constant(self):
        Ll = self.inductance_per_length()
        Cl = self.capacitance_per_length()
        return self.__fo * np.sqrt(Ll*Cl)