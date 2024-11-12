"""
Scripts for calculating all properties of an option


"""




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
N_prime = norm.pdf
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
        self.iv = sigma
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
        return self.iv/100
    
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
    #print out parameters
    def params(self):
        return {'call or put':self.cp,
                'underlying price': self.S, 
                'strike': self.K, 
                'days til expiry': self.tte, 
                'IV (%)':self.iv,
                'risk-free rate (%)':self.rate,
                'annual dividend (%)':self.q*100
                }
                
   
    
    #====calculates commonly used functions in Black-Scholes====#
    @property
    def div_decay(self):
        return np.exp(-self.q*self.T)
    
    @property
    def rf_decay(self):
        return np.exp(-self.r*self.T)
    
    @property
    def d1(self):
        """
        Calculates the d1 function of Black Scholes Model.
        
        NOTES:
            N(d1): the probability that the option will be in-the-money at expiration, 
            adjusted for the present value of the exercise price. It accounts for the expected growth of the stock price.
        """
        p1 = np.log(self.S / self.K) #log ratio of strike to current price
        p2 = (self.r - self.q + self.sigma**2/2)*self.T #rate of price diffusion
        p3 = self.sigma * np.sqrt(self.T) #decay over time
        d1 = (p1 + p2)/p3
        return d1
    
    @property
    def d2(self):
        """
        Calculates the d2 function of Black Scholes Model.

        NOTES:
            N(d2): the risk-neutral probability that the option will be exercised 
            (i.e., that the stock price will be above the strike price at expiration).
        """
        d2 = self.d1 - (self.sigma * np.sqrt(self.T))
        return d2
    
    
    #====calculate the options' price====#
    @property
    def price(self):
        """
        Calculates the price of a option.
        """
        if self.cp == self.c:   
            #calculate call price
            p1 = self.S *self.div_decay* N(self.d1)
            p2 = self.K * self.rf_decay * N(self.d2)
            price =  p1 - p2   
            return price
        
        elif self.cp == self.p:
            #calculate put price
            p1 = self.S*self.div_decay*N(-self.d1)
            p2 = self.K * self.rf_decay * N(-self.d2)
            price =  -p1 + p2
            return price
        
        else:
            self.not_cp

    
    #====calculate the options' greeks====#
    @property
    def delta(self):
        """
        Calculates the delta of an option.
        
        delta: derivative of price w.r.t. to S
        """
        #call option
        if self.cp == self.c:   
            return self.div_decay*N(self.d1)
        
        #put option
        elif self.cp == self.p:
            return self.div_decay*N(self.d1) - 1
        
        else:
            self.not_cp
    @property
    def gamma(self):
        """
        Calculates the gamma of an option.
        
        gamma: derivate of delta w.r.t. S
            also equals to the second derivative of price w.r.t. S

        NOTES: 
            The results are the same for call and put
        """
        return self.div_decay * N_prime(self.d1) / (self.S * self.sigma * np.sqrt(self.T))

    @property
    def vega(self):
        """
        Calculates the vega of an option.

        veta: derivate of price w.r.t. IV
        
        NOTES: 
            The results are the same for call and put
        """
        return self.div_decay * self.S * np.sqrt(self.T) * N_prime(self.d1) / 100
    
    @property
    def theta(self):
        """
        Calculates the theta of an option.

        theta: derivate of price w.r.t. time
        """
        #calculate the current expected probability the stock will be at a certain price
        p1 = (-self.S * N_prime(self.d1) * self.sigma) / (2 * np.sqrt(self.T))

        #call option
        if self.cp == self.c:
            #calculates the time value based on the chance the option will expire ITM
            p2 = self.r * self.K * self.rf_decay * N(self.d2)
            p3 = self.q * self.S * self.div_decay * N(self.d1)
            return (p1 - p2 + p3)/365.0
        
        #put option
        elif self.cp == self.p:
            #calculates the time value based on the chance the option will expire ITM
            p2 = self.r * self.K* np.exp(-self.r*self.T)* N(-self.d2) 
            p3 = self.q * self.S * self.div_decay * N(-self.d1)
            return (p1 + p2 - p3)/365.0
        
        else:
            self.not_cp
    
    @property
    def rho(self):
        """
        Calculates the rho of an option.

        rho: derivate of price w.r.t. interest rate
        """
        #call option
        if self.cp == self.c:   
            return self.rf_decay * self.K * self.T * N(self.d2) / 100
        
        #put option
        elif self.cp == self.p:
            return -self.rf_decay * self.K * self.T * N(-self.d2) / 100
        
        else:
            self.not_cp


    def impVol():
        return 1
    
    @property
    #print out the important greeks
    def greeks(self):
        return {
                'price': self.price,
                'IV (%)': self.iv,
                'delta':self.delta,
                'theta': self.theta,
                'gamma':self.gamma,
                }
    
    @property
    #print out all of the greeks
    def greeksfull(self):
        return {
                'price': self.price,
                'IV (%)': self.iv,
                'delta':self.delta,
                'theta': self.theta,
                'gamma':self.gamma,
                'vega':self.vega,
                'rho':self.rho
                }

