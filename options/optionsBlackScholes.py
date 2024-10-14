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
    
    #initialize class
    def __init__(self, cp, S, K, T, sigma, r = rf_rates, q=0):
        """
        Initialize parameters.
        
        cp: calls or puts.
        S: underlying price.
        K: options strike price.
        T: Time until expiry (days).
        sigma: implied volatility of the options as a percentage, i.e. 100% IV = 100
        r: risk free rates. Default 3mo T-bill yield.
        q: dividend of underlying in dollars. Default zero.
        """
        self.callput = cp
        self.S = S
        self.K = K
        self.tte = T
        self.sig = sigma
        self.rate = r
        self.dividend = q
    
    #=====define fixed variables and functions=====#
    @property
    def cp(self):
        cp = self.callput.upper()
        if cp == "C" or cp == "CALL" or cp == "CALLS":
            return self.c
        elif cp == "P" or cp == "PUT" or cp == "PUTS":
            return self.p
        else:
            self.not_cp
    
    @property
    def sigma(self):
        return self.sig/100
    
    @property
    def r(self):
        return self.rate/100
    
    @property
    def q(self):
        return self.dividend*4/self.S
    
    @property
    def T(self):
        #limit T so you do not get divide by zero error
        if self.tte < 0.000001:
            return 0.000001
        else:
            return self.tte/365.0
    
    @property
    def div_decay(self):
        return np.exp(-self.q*self.T)
    
    @property
    def rf_decay(self):
        return np.exp(-self.r*self.T)
            
    @property
    #print out parameters
    def params(self):
        return {'call or put':self.cp,
                'underlying price': self.S, 
                'strike': self.K, 
                'days til expiry': self.tte, 
                'IV (%)':self.sig,
                'risk-free rate (%)':self.rate,
                'annual dividend (%)':self.q
                }
                
   
    
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


