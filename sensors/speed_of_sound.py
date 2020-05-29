import math

def calculate_c(temperature, relative_humidity, pressure_hPa = 101.325):
    """
    Code from: Dr Richard Lord - http://www.npl.co.uk/acoustics/techguides/speedair
    Based on the approximate formula found in
    Owen Cramer, "The variation of the specific heat ratio and the speed of sound in air with temperature, pressure, humidity, and CO2 concentration",
    The Journal of the Acoustical Society of America (JASA), J. Acoust. Soc. Am. 93(5) p. 2510-2516; formula at p. 2514.
    Saturation vapour pressure found in
    Richard S. Davis, "Equation for the Determination of the Density of Moist Air (1981/91)", Metrologia, 29, p. 67-70, 1992,
    and a mole fraction of carbon dioxide of 0.0004.
    The mole fraction is simply an expression of the number of moles of a compound divided by the total number of moles of all the compounds present in the gas.
    """
    
    T = temperature
    Rh = relative_humidity
    Kelvin = 273.15

    P = pressure_hPa * 1000

    T_kel = Kelvin + T

    sqrT = T * T
    sqrT_kel = T_kel * T_kel

    # Molecular concentration of water vapour calculated from Rh
    # using Giacomos method by Davis (1991) as implemented in DTU report 11b-1997
    ENH = 3.14e-8 * P + 1.00062 + sqrT * 5.6e-7

    # These commented lines correspond to values used in Cramer (Appendix)
    # PSV1 = sqr(T_kel)*1.2811805*math.pow(10,-5)-1.9509874*math.pow(10,-2)*T_kel ;
    # PSV2 = 34.04926034-6.3536311*math.pow(10,3)/T_kel;
    PSV1 = sqrT_kel * 1.2378847e-5 - 1.9121316e-2 * T_kel
    PSV2 = 33.93711047 - 6343.1645 / T_kel

    PSV = math.exp(PSV1) * math.exp(PSV2)

    H = Rh * ENH * PSV / P
    Xw = H / 100.0

    # Xc = 314.0e-6
    Xc = 400e-6

    # Speed calculated using the method of Cramer from
    # JASA vol 93 pg 2510
    C1 = (
        0.603055 * T + 331.5024
        - sqrT * 5.28e-4
        + (0.1495874 * T + 51.471935 - sqrT * 7.82e-4) * Xw
    )
    C2 = (
        (
            -1.82e-7 + 3.73e-8 * T
            -sqrT * 2.93e-10
        ) * P
        + (
            -85.20931
            - 0.228525 * T
            + sqrT * 5.91e-5
        ) * Xc
    )
    C3 = (
        Xw * Xw * 2.835149
        + P * P * 2.15e-13
        - Xc * Xc * 29.179762
        - 4.86e-4 * Xw * P * Xc
    )
    C = C1 + C2 - C3

    return C
