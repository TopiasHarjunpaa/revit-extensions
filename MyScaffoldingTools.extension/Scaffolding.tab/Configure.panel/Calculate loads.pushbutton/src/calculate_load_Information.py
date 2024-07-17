# -*- coding: utf-8 -*-

import math
from pyrevit import revit, DB

WALL_PRESSURE = 0.8
WALL_SUCTION = -0.5
MONOPITCH_SUCTION_US = -0.6
MONOPITCH_SUCTION_DS = -0.9
Z_ZERO = [0.003, 0.01, 0.05, 0.3, 1]
Z_MIN = [1, 1, 2, 5, 10]
TERRAIN_FACTOR_FIN = 0.18

def calculate_propability_factor(return_period, shape_parameter=0.2, cprob_exponent=0.5):
    """Probability factor is used to modify fundamental basic wind velocity vb which has mean return period
        of 50 years. The 10 minutes mean wind velocity having the probability p for an annual exceedence is determined
        by multiplying the fundamental basic wind velocity vb by the probability factor, cprob.
        It is calculated using the following expression given at EN 1911-1-4 (expression 4.2):

        cprob = (1 - K ⋅ ln(-ln(1 - p)) / 1 - K ⋅ ln(-ln(0.98)))^n  where:

        K is the shape parameter
        n is exponent
        p is probability for an annual exceedence

        NOTE: Return period has been limited to min 2 years, due value 1 or less will lead into error -> ln(0)

    Args:
        return_period (int): Return period in years to calculate probability for an annual exceedence.
        shape_parameter (float, optional): Parameter depending on the coefficient of variation of the extreme-value distribution. Defaults to 0.2.
        cprob_exponent (float, optional): Exponent of the expression. Defaults to 0.5.

    Returns:
        float: Probability factor to modify fundamental basic wind velocity
    """

    rp = max(return_period, 2)
    
    inner_log_divident = math.log(1 - 1.0 / rp)
    outer_log_divident = math.log(-1 * inner_log_divident)
    divident = 1 - shape_parameter * outer_log_divident
    
    inner_log_divider = math.log(1 - 1.0 / 50)
    outer_log_divider = math.log(-1 * inner_log_divider)
    divider = 1 - shape_parameter * outer_log_divider
    
    cprob = (divident / divider) ** cprob_exponent
    
    return cprob

def calculate_terrain_factor(fin, terrain_category):
    """Terrain factor is calculated using formula kr = 0.19 ⋅ (z0 / z0,II) ^ 0.07
        where:

        z0      is roughness length depended on the terrain category
        z0,II   is roughness length on the terrain category II

        Exception:

        Terrain factor should be 0.18 in Finland at terrain category 0. Explanation in finnish NA:

        "Tuulen nopeudet merialueilla tulevat aliarvioiduiksi, jos lauseketta (4.5) sovelletaan 
        maastokertoimen arviointiin. Tämän takia maastokertoimelle sovelletaan merialueilla 
        arvoa kr =0,18, joka perustuu tilastoaineistoon.
    Args:
        fin (bool): Boolean determine whether finnish NA should be followed or not. 
        terrain_category (int): Terrain category used in a calculation. Integer between 0 - 4.

    Returns:
        float: Terrain factor used in further wind load calculations
    """

    if fin and terrain_category == 0:
        return TERRAIN_FACTOR_FIN
    return 0.19 * (Z_ZERO[terrain_category]/Z_ZERO[2]) ** 0.07

def convert_pressure_to_speed(pressure, air_density):
    """Converts wind pressure to wind speed using the expression qp = 0.5 ⋅ p ⋅ (vb)^2 which
        is modified into form of:

        vb = sqrt(1000 * qp * 2 / p)

        Expression uses wind pressure in form of N/m2 and therefore pressure recieved in argument
        will be converted in same form by multiplying it with the value of 1000. (1 kN/m2 = 1000 N/m2).

    Args:
        pressure (float): Wind pressure in form of kN/m2
        air_density (float): Air density depends on the altitude, temperature and barometric pressure.

    Returns:
        float: _description_
    """

    return math.sqrt((1000 * pressure * 2) / air_density)

def calculate_peak_velocity_pressure(
    fin, 
    terrain_category,
    return_period,
    height,
    fundamental_basic_wind_velocity,
    seasonal_factor=1.0,
    orography_factor=1.0,
    air_density=1.25,
    directional_factor=1.0,
    turbulence_factor=1.0
):
    """Calculate peak wind velocity pressure according to EN 1991-1-4.
        Process involves following steps:

        1. Calculate probability factor
        2. Modify fundamental basic wind velocity: vb = cdir · cseason · vb,0 · cprob
        3. Calculate terrain factor: kr = 0.19 ⋅ (z0 / z0,II)^0.07
        4. Calculate roughness factor: cr(ze) = kr ⋅ ln(max{ze, zmin} / z0)
        5. Calculate mean wind velocity: vm(ze) = cr(ze) ⋅ c0(ze) ⋅ vb
        6. Calculate turbulence intensity: Iv(ze) = kI / (c0(ze) ⋅ ln(max{ze, zmin} / z0))
        7. Calculate peak velocity pressure: qp(ze) = (1 + 7 ⋅ Iv(ze)) ⋅ (1/2) ⋅ p ⋅ vm(ze)2

    Args:
        fin (bool): To determine whether finnish NA needs to be used or not.
        terrain_category (int): Value between 0 - 4 to determine roughness and turbulence factors.
        return_period (float): Return period in years to calculate probability for an annual exceedence.
        height (float): Structure height from the ground in meters.
        fundamental_basic_wind_velocity (float): is the fundamental value of the basic wind velocity in m/s. 
        seasonal_factor (float, optional): The value of seasonal factor. May be given in the NA. Defaults to 1.0.
        orography_factor (float, optional): Orography factor, taken as 1,0 unless otherwise specified in 4.3.3. Defaults to 1.0.
        air_density (float, optional): Air density depends on the altitude, temperature and barometric pressure. Defaults to 1.25.
        directional_factor (float, optional): The value of directional factor. May be given in the NA. Defaults to 1.0.
        turbulence_factor (float, optional): The value of the turbulence factor. May be given in the NA. Defaults to 1.0.

    Returns:
        dict: Returns dictionary of wind parameters and calculation results from various expression.
    """

    wind_height = max(min(200, height), Z_MIN[terrain_category])
    cprob = calculate_propability_factor(return_period)
    basic_wind_velocity = fundamental_basic_wind_velocity * cprob * seasonal_factor * directional_factor
    terrain_factor = calculate_terrain_factor(fin, terrain_category)
    roughness_factor = terrain_factor * math.log(wind_height / Z_ZERO[terrain_category])
    mean_wind_velocity = roughness_factor * orography_factor * basic_wind_velocity
    wind_turbulence = turbulence_factor / (orography_factor * math.log(wind_height / Z_ZERO[terrain_category]))
    peak_velocity_pressure = (1 + 7 * wind_turbulence) * 1/2000 * air_density * mean_wind_velocity ** 2
    peak_wind_speed = convert_pressure_to_speed(peak_velocity_pressure, air_density)

    return {
        "Directional factor": directional_factor,
        "Seasonal factor": seasonal_factor,
        "Probability factor": cprob,
        "Fundamental basic wind velocity": fundamental_basic_wind_velocity,
        "Basic wind velocity": basic_wind_velocity,
        "Mean wind velocity": mean_wind_velocity,
        "Roughness factor": roughness_factor,
        "Wind turbulence intensity": wind_turbulence,
        "Orography factor": orography_factor,
        "Turbulence factor": turbulence_factor,
        "Air density": air_density,
        "Peak velocity pressure": peak_velocity_pressure,
        "Peak wind speed": peak_wind_speed
    }

def calculate_roof_suction(angle, width):
    """Calculate external roof suction pressure coefficient according to EN 16508
        using roof angle and roof width.

    Args:
        angle (int): Roof angle in degrees.
        width (int): Roof width in millimeters.

    Returns:
        float: Roof suction pressure coefficient.
    """

    angle_factor = min(max((angle - 10) / 100, 0), 0.1)
    if width <= 10000:
        return -0.7 + angle_factor
    elif width < 25000:
        return 0.01 * width / 1000 - 0.8 + angle_factor
    return -0.55 + angle_factor

def calculate_pressure_coefficents(angle, width):
    """Calculate pressure coefficients for weather protection according to EN 16508
        using roof angle and roof width. Sets roof pressure coefficients to zero if roof width
        has set to zero.

    Args:
        angle (int): Roof angle in degrees.
        width (int): Roof width in millimeters.

    Returns:
        dict: Pressure coefficients in dictionary format. Key = name of the pressure surface. Value = coefficient.
    """

    coefficients = {}
    coefficients["Wall pressure"] = WALL_PRESSURE
    coefficients["Wall suction"] = WALL_SUCTION
    coefficients["Roof pressure"] = min(max(0.03 * angle - 0.25, 0), 0.7)
    coefficients["Double-pitch roof suction"] = calculate_roof_suction(angle, width)
    coefficients["Mono-pitch roof suction to up slope"] = MONOPITCH_SUCTION_US
    coefficients["Mono-pitch roof suction to down slope"] = MONOPITCH_SUCTION_DS
    if width == 0:
        coefficients["Roof pressure"] = 0.0
        coefficients["Double-pitch roof suction"] = 0.0
        coefficients["Mono-pitch roof suction to up slope"] = 0.0
        coefficients["Mono-pitch roof suction to down slope"] = 0.0   
    return coefficients

def format_imposed_loads(imposed_load):
    """Formats response according to imposed load value. Includes imposed load
        and combination factor based on EN 12811-1. Converts imposed load value from kilograms to kilonewtons.

    Args:
        imposed_load (float): Imposed load in kilograms.

    Returns:
        dict: Multiline string of the imposed load information.
    """

    combination_factor = "1,00"
    if imposed_load <= 75:
        combination_factor = "0,00"
    if 75 < imposed_load <= 200:
        combination_factor = "0,25"
    if 200 < imposed_load <= 600:
        combination_factor = "0,50"

    return {"Imposed loads": "{:.2f}".format(imposed_load / 100).replace(".", ","), "Imposed load combination factor": combination_factor}

def format_consequence_class(consequence_class):
    """Calculates K factor according to consequence class based on EN 1990 and creates response
        in dictionary format.

    Args:
        consequence_class (int): Consequence class (CC1, CC2, or CC3)

    Returns:
        dict: Dictionary where key is formatted consequence class and value is K factor.
    """

    k_factor = "1,00"
    if (consequence_class == 1):
        k_factor = "0,90"
    if (consequence_class == 3):
        k_factor = "1,10"

    return {"Consequence class": "CC{}".format(consequence_class), "K factor": k_factor}

def format_load_parameters(
    wind_calculation_params,
    pressure_coefficients,
    angle,
    bay_length,
    roof_width,
    return_period,
    height,
    imposed_load,
    consequence_class,
    snow_load,
    terrain_category
):
    """Formats input with calculate parameters. These will be used as Revit parameters.

    Returns:
        dict: A dictionary containing parameter name as key and formated parameter value as value.
    """

    formatted_load_params = {key: "{:.2f}".format(float(value)).replace(".", ",") for key, value in wind_calculation_params.items()}
    formatted_load_params.update(format_imposed_loads(imposed_load))
    formatted_load_params.update(format_consequence_class(consequence_class))
    line_load = wind_calculation_params["Peak velocity pressure"] * bay_length / 1000

    for key, value in pressure_coefficients.items():
        formatted_load_params[key] = "{:.2f}".format(value).replace(".", ",")
        formatted_load_params["{} load".format(key)] = "{:.2f}".format(value * line_load).replace(".", ",")

    formatted_load_params["Terrain category"] = ["0", "I", "II", "III", "IV"][terrain_category]
    formatted_load_params["Roof angle"] = "{:.2f}".format(float(angle)).replace(".", ",")
    formatted_load_params["Bay length"] = "{:.2f}".format(bay_length / 1000).replace(".", ",")
    formatted_load_params["Roof width"] = "{:.2f}".format(roof_width / 1000).replace(".", ",")
    formatted_load_params["Snow load"] = "{:.2f}".format(snow_load / 100).replace(".", ",")
    formatted_load_params["Return period"] = "{:.0f}".format(return_period).replace(".", ",")
    formatted_load_params["Height above ground"] = "{:.0f}".format(height).replace(".", ",")

    return formatted_load_params

def calculate_load_information(load_input):
    finnish_na = True if load_input["A1"] == 1 else False
    imposed_load = load_input["A2"]
    snow_load = load_input["A3"]
    consequence_class = load_input["A4"]
    fundamental_basic_wind_velocity = load_input["B1"]
    terrain_category = load_input["B2"]
    return_period = load_input["B3"]
    seasonal_factor = load_input["B4"]
    orography_factor = load_input["B5"]
    height = load_input["C1"]
    roof_width = load_input["C2"]
    bay_length = load_input["C3"]
    angle = 0 if roof_width == 0 else load_input["C4"]

    wind_calculation_params = calculate_peak_velocity_pressure(
        finnish_na,
        terrain_category,
        return_period, height,
        fundamental_basic_wind_velocity,
        seasonal_factor,
        orography_factor
    )

    pressure_coefficients = calculate_pressure_coefficents(angle, roof_width)

    return format_load_parameters(
        wind_calculation_params,
        pressure_coefficients,
        angle,
        bay_length,
        roof_width,
        return_period,
        height,
        imposed_load,
        consequence_class,
        snow_load,
        terrain_category
    )
