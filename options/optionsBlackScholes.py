if __name__ == '__main__':
    #mimics relative import when run as a script
    import sys
    import os
    
    # Find the grandparent directory path (two levels up from the current script)
    grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Add the grandparent directory to sys.path
    sys.path.insert(0, grandparent_dir)

import numpy as np
from scipy.stats import norm
from fundamentals.riskFreeRate import risk_free_rate

#easy function access
N = norm.cdf
rf_rates = risk_free_rate()

class options:
    #define fixed variables
    c = 'calls'
    p = 'puts'
    def not_cp():
        raise Exception("Error: not a put or call.")
        
    def __init__(self, cp, S, K, T, sigma, r = rf_rates, q=0):
        """
        Initialize parameters.
        
        cp: calls or puts.
        S: underlying price.
        K: options strike price.
        T: Time until expiry (days).
        sigma: implied volatility of the options as a decimal, i.e. 100% IV = 1
        r: risk free rates. Default 3mo T-bill yield.
        q: dividend of underlying in dollars. Default zero.
        """
        self.S = S
        self.K = K
        self.tte = T
        self.sigma = sigma/100
        self.r = r/100
        self.q = q*4/S
        
        #simplify defining type, as calls or puts
        cp = cp.upper()
        if cp == "C" or cp == "CALL" or cp == "CALLS":
            self.cp = self.c
        elif cp == "P" or cp == "PUT" or cp == "PUTS":
            self.cp = self.p
        else:
            self.not_cp
            
        #limit T so you do not get divide by zero error
        if self.tte < 0.000001:
            self.T = 0.000001
        else:
            self.T = self.tte/365.0
         
    @property
    #print out parameters
    def params(self):
        return {'cp':self.cp,
                'S': self.S, 
                'K': self.K, 
                'T': self.tte, 
                'r':self.r,
                'q':self.q,
                'sigma':self.sigma}
    
    #define fixed functions
    
    @property
    def div_decay(self):
        return np.exp(-self.q*self.T)
    
    @property
    def rf_decay(self):
        return np.exp(-self.r*self.T)
    
    
    #====calculates the d-functions in Black-Scholes====#
    @property
    def d1(self):
        """
        Calculates the d1 function of Black Scholes Model.
        """
        d1 = (np.log(self.S/self.K) + (self.r - self.q + self.sigma**2/2)*self.T) \
            /(self.sigma*np.sqrt(self.T))
        return d1
    @property
    def d2(self):
        """
        Calculates the d1 function of Black Scholes Model.
        """
        d2 = self.d1 - (self.sigma*np.sqrt(self.T))
        return d2

    #====calculate the options' price====#
    def price(self):
        '''
        Calculates the price of a option.
        '''
        if self.cp == self.c:   
            #calculate call price
            price = self.S *np.exp(-self.q*self.T)* N(self.d1) - \
                self.K * np.exp(-self.r*self.T) * N(self.d2)
            return price
        elif self.cp == self.p:
            #calculate put price
            price = self.K * np.exp(-self.r * self.T) * N(-self.d2) - \
                self.S*np.exp(-self.q*self.T)*N(-self.d1)
            return price
        else:
            self.not_cp


    #====calculate the options' greeks====#
    def delta(self):
        '''
        Calculates the Delta of a option
        '''
        #call option
        if self.cp == self.c:   
            return self.div_decay*N(self.d1)
        
        #put option
        elif self.cp == self.p:
            return self.div_decay*N(self.d1) - 1
        
        else:
            self.not_cp
            
    def gamma(self):
        """
        Calculates the Gamma of a option
        *******
        WIP
        ********
        """
        #call option
        if self.cp == self.c:   
            return self.div_decay*N(self.d1)
        
        #put option
        elif self.cp == self.p:
            return -self.div_decay*N(self.d1)
        
        else:
            self.not_cp
            
    def impVol():
        return 1


